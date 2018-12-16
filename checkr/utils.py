import json
import os
import re
import shutil
import subprocess
import zipfile

import requests
from django.conf import settings

from checkr.models import GithubAudit, ZipAudit
from checkr.web3 import broadcast_audit_result

# Constant strings
CONTRACT_FILENAME = 'contract.sol'
REPORT_FILENAME = 'report.json'


def analyze_contract(contract):
    """Analyze a single contract."""
    if contract:
        # temporarily write a .sol file for Slither to check
        # TODO: Find better approach
        with open(CONTRACT_FILENAME, 'w') as f:
            f.write(contract)

        # use Slither through subprocess
        terminal_audit = subprocess.run(
            ['slither', CONTRACT_FILENAME, '--exclude', 'naming-convention',
             '--json', REPORT_FILENAME],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        audit_report = terminal_audit.stdout.decode('utf-8').strip()

        if os.path.exists(CONTRACT_FILENAME):
            os.remove(CONTRACT_FILENAME)

        json_report = ''
        if os.path.exists(REPORT_FILENAME):
            with open(REPORT_FILENAME, 'r') as f:
                json_report = json.loads(f.read())
            os.remove(REPORT_FILENAME)

        if 'Compilation warnings/errors' in audit_report:
            limiter = '\nINFO:Detectors' if '\nINFO:Detectors' in audit_report else '\nINFO:Slither'
            err_regex = re.compile(r'{}:(\d)+:(\d)+: (Warning|Error):'.format(CONTRACT_FILENAME))
            err_indeces = [item.span() for item in re.finditer(err_regex, audit_report)]
            err_list = []
            has_error = False

            for i, item in enumerate(err_indeces):
                item_detail = ''
                if i == len(err_indeces) - 1:
                    item_detail = audit_report[item[1]:audit_report.find(limiter)].strip()
                else:
                    item_detail = audit_report[item[1]:err_indeces[i + 1][0]].strip()

                broken_string = audit_report[item[0]:item[1]].split(':')
                if broken_string[3].strip() == 'Error':
                    has_error = True

                err_list.append({
                    'line': broken_string[1],
                    'character': broken_string[2],
                    'type': broken_string[3].strip(),
                    'detail': item_detail
                })

            return {
                'success': not has_error,
                'error': has_error,
                'audit_type': 'contract',
                'detail_list': err_list,
                'issues': json_report
            }

        return {
            'success': True,
            'error': False,
            'audit_type': 'contract',
            'filename': CONTRACT_FILENAME,
            'issues': json_report
        }

    return None


def initialize_directory(repo_name):
    if repo_name:
        folder_name = repo_name.replace('/', '+')

        if not os.path.exists('contracts'):
            os.mkdir('contracts')

        save_path = os.path.join('contracts', folder_name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        else:
            pass

        return save_path
    return None


def get_contracts_from_list(save_path, repo_name, file_list=None, session=None):
    """Download all contracts within an array of GitHub files. Then return list of contract data."""
    github_raw_api = 'https://raw.githubusercontent.com/{}/master/'.format(repo_name)

    contract_list = {}
    if file_list and session:
        # Download each file from the list
        for file in file_list:
            file_data = session.get('{}{}'.format(github_raw_api, file.get('path')))
            with open(os.path.join(save_path, file.get('name')), 'wb') as f:
                f.write(file_data.content)

            contract_list[file.get('name')] = file_data.text
        return contract_list
    return None


def analyze_repository(repository=None, tracking=None, author=None):
    """Get all Solidity files from a GitHub repository and analyze"""
    if repository and tracking and author:
        # GitHub API URLs
        github_api = 'https://api.github.com/search/code?q=extension:sol+repo:'
        github_url = '{}{}'.format(github_api, repository)

        # Initialize a requests.Session() instance with User-Agent header
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36(KHTML, like Gecko) '
                          'Chrome/43.0.2357.134 Safari/537.36'
        })

        # Initialize new GithubAudit instance
        save_path = initialize_directory(repository)
        github_audit_instance = GithubAudit(
            repo=repository,
            tracking=tracking,
            author=author,
        )

        # Fetch Solidity file list from GitHub API
        all_contracts = {}
        response = session.get('{}{}'.format(github_api, repository))
        if response.status_code == 200 and response.text:
            response_json = json.loads(response.text)

            if response_json.get('total_count') > 0:
                # download all contracts from first page, save directory
                all_contracts.update(get_contracts_from_list(
                    save_path,
                    repository,
                    response_json.get('items'),
                    session
                ))

                # download all contracts all other pages
                contracts = response_json.get('total_count')
                if contracts > 30:
                    pages = int(contracts / 30) + 1  # ex. 100 / 30 = 3.33 means 4 pages
                    for page in range(2, pages + 1):  # start iterating from 2nd page
                        page_response = session.get('{}&page={}'.format(github_url, page))
                        page_response_json = json.loads(page_response.text)
                        if page_response_json.get('items'):
                            all_contracts.update(get_contracts_from_list(
                                save_path,
                                repository,
                                page_response_json.get('items'),
                                session
                            ))

        # Audit downloaded files
        terminal_audit = subprocess.run(
            ['slither', save_path, '--exclude', 'naming-convention',
             '--json', REPORT_FILENAME],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        audit_report = terminal_audit.stdout.decode('utf-8').strip()

        json_report = ''
        if os.path.exists(REPORT_FILENAME):
            with open(REPORT_FILENAME, 'r') as f:
                json_report = json.loads(f.read())
                github_audit_instance.report = json_report
            os.remove(REPORT_FILENAME)

        if 'Compilation warnings/errors' in audit_report:
            contract_names = '|'.join(all_contracts.keys())
            limiter = '\nINFO:Detectors' if '\nINFO:Detectors' in audit_report else '\nINFO:Slither'
            err_regex = re.compile(r'({}):(\d)+:(\d)+: (Warning|Error):'.format(contract_names))
            err_indeces = [item.span() for item in re.finditer(err_regex, audit_report)]
            err_list = []
            has_error = False

            for i, item in enumerate(err_indeces):
                item_detail = ''
                if i == len(err_indeces) - 1:
                    item_detail = audit_report[item[1]:audit_report.find(limiter)].strip()
                else:
                    item_detail = audit_report[item[1]:err_indeces[i + 1][0]].strip()

                broken_string = audit_report[item[0]:item[1]].split(':')
                if broken_string[3].strip() == 'Error':
                    has_error = True

                err_list.append({
                    'contract': broken_string[0],
                    'line': broken_string[1],
                    'character': broken_string[2],
                    'type': broken_string[3].strip(),
                    'detail': item_detail
                })

            if has_error:
                shutil.rmtree(save_path, ignore_errors=True)
                return {
                    'success': not has_error,
                    'error': has_error,
                    'audit_type': 'repository',
                    'detail_list': err_list
                }

        passed_test = True  # passed or failed test
        for issue in json_report:
            if issue.get('impact_level') < 3:
                passed_test = False
                break

        github_audit_instance.contracts = json.dumps(all_contracts)
        github_audit_instance.result = passed_test
        github_audit_instance.save()

        # Broadcast result to blockchain
        broadcast_audit_result(tracking, passed_test)

        # clean saved files
        shutil.rmtree(save_path, ignore_errors=True)

        return {
            'success': True,
            'error': False,
            'audit_type': 'repository',
            'contracts': all_contracts,
            'tracking': github_audit_instance.tracking,
            'repo': repository,
            'issues': json_report
        }

    return None


def analyze_zip(file=None, tracking=None, author=None):
    if file and tracking and author:
        extracted_dir = 'extracted'
        zip_dir = 'zipcontracts'
        zip_report = 'zipreport.json'
        if not os.path.exists(zip_dir):
            os.mkdir(zip_dir)

        if not os.path.exists(extracted_dir):
            os.mkdir(extracted_dir)

        all_contracts = {}
        shutil.move(file.temporary_file_path(), os.path.join(zip_dir, file.name))
        with zipfile.ZipFile(os.path.join(zip_dir, file.name), 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)

        for root, dirs, files in os.walk(extracted_dir):
            for name in files:
                if os.path.splitext(name)[1] == '.sol':
                    with open(os.path.join(root, name), 'r') as f:
                        all_contracts[name] = f.read()
                    shutil.move(os.path.join(root, name), zip_dir)

        terminal_audit = subprocess.run(
            ['slither', zip_dir, '--exclude', 'naming-convention',
             '--json', zip_report],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        audit_report = terminal_audit.stdout.decode('utf-8').strip()
        zip_audit_instance = ZipAudit(
            contracts=json.dumps(all_contracts),
            tracking=tracking,
            author=author,
        )

        if 'Compilation warnings/errors' in audit_report:
            contract_names = '|'.join(all_contracts.keys())
            limiter = '\nINFO:Detectors' if '\nINFO:Detectors' in audit_report else '\nINFO:Slither'
            err_regex = re.compile(r'({}):(\d)+:(\d)+: (Warning|Error):'.format(contract_names))
            err_indeces = [item.span() for item in re.finditer(err_regex, audit_report)]
            err_list = []
            has_error = False

            for i, item in enumerate(err_indeces):
                item_detail = ''
                if i == len(err_indeces) - 1:
                    item_detail = audit_report[item[1]:audit_report.find(limiter)].strip()
                else:
                    item_detail = audit_report[item[1]:err_indeces[i + 1][0]].strip()

                broken_string = audit_report[item[0]:item[1]].split(':')
                if broken_string[3].strip() == 'Error':
                    has_error = True

                err_list.append({
                    'contract': broken_string[0],
                    'line': broken_string[1],
                    'character': broken_string[2],
                    'type': broken_string[3].strip(),
                    'detail': item_detail
                })

            if has_error:
                shutil.rmtree(zip_dir, ignore_errors=True)
                shutil.rmtree(extracted_dir, ignore_errors=True)

                return {
                    'success': not has_error,
                    'error': has_error,
                    'audit_type': 'zip',
                    'detail_list': err_list
                }

        json_report = ''
        if os.path.exists(zip_report):
            with open(zip_report, 'r') as f:
                json_report = json.loads(f.read())
                zip_audit_instance.report = json_report
            os.remove(zip_report)

        passed_test = True  # passed or failed test
        for issue in json_report:
            if issue.get('impact_level') < 3:
                passed_test = False
                break

        zip_audit_instance.result = passed_test
        zip_audit_instance.save()

        # Broadcast result to blockchain
        broadcast_audit_result(tracking, passed_test)

        # clean saved files
        shutil.rmtree(zip_dir, ignore_errors=True)
        shutil.rmtree(extracted_dir, ignore_errors=True)

        return {
            'success': True,
            'error': False,
            'audit_type': 'zip',
            'contracts': all_contracts,
            'tracking': tracking,
            'issues': json_report
        }

    return None
