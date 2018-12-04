import ast
import json
import os
import shutil
import subprocess

import requests
from django.conf import settings

from checkr.models import GithubAudit

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
            ["slither", CONTRACT_FILENAME, "--json", REPORT_FILENAME],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        audit_report = terminal_audit.stdout.decode("utf-8").strip()

        if os.path.exists(CONTRACT_FILENAME):
            os.remove(CONTRACT_FILENAME)

        json_report = ''
        if os.path.exists(REPORT_FILENAME):
            with open(REPORT_FILENAME, 'r') as f:
                json_report = ast.literal_eval(f.read())
            os.remove(REPORT_FILENAME)

        if 'Compilation warnings/errors' in audit_report:
            # temporary bad way of parsing error into something like
            # '8:21: Error: Expected primary expression.'
            b = audit_report[audit_report.find(CONTRACT_FILENAME) +
                             1:audit_report.rfind('\n\nINFO')]
            broken_string = b[b.find(CONTRACT_FILENAME):]

            separated_list = broken_string.split(':')
            error_desc = ' '.join([x.strip() for x in separated_list[4:]])

            return {
                'success': False,
                'error': True,
                'audit_type': 'contract',
                'filename': CONTRACT_FILENAME,
                'lineno': int(separated_list[1]),
                'character': int(separated_list[2]),
                'details': error_desc[:error_desc.index('\x1b[0m\n')].strip(),
                'code': error_desc[error_desc.index('\x1b[0m\n') +
                                   len('\x1b[0m\n'):]
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


def analyze_repository(repository=None):
    """Get all Solidity files from a GitHub repository and analyze"""
    if repository:
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
        github_audit_instance = GithubAudit(repo=repository)

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
            ['slither', save_path, '--json', REPORT_FILENAME],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        audit_report = terminal_audit.stdout.decode("utf-8").strip()

        json_report = ''
        if os.path.exists(REPORT_FILENAME):
            with open(REPORT_FILENAME, 'r') as f:
                github_audit_instance.report = f.read()
                json_report = ast.literal_eval(github_audit_instance.report)
            os.remove(REPORT_FILENAME)

        passed_test = True  # passed or failed test
        for issue in json_report:
            if issue.get('severity') < 3:
                passed_test = False
                break

        github_audit_instance.contracts = json.dumps(all_contracts)
        github_audit_instance.result = passed_test
        github_audit_instance.save()

        # clean saved files
        if os.path.exists(save_path):
            shutil.rmtree(save_path, ignore_errors=True)

        if 'Compilation warnings/errors' in audit_report:
            # TODO!!!
            # temporary bad way of parsing error into something like
            # '8:21: Error: Expected primary expression.'
            # b = audit_report[audit_report.find(CONTRACT_FILENAME) +
            #                  1:audit_report.rfind('\n\nINFO')]
            # broken_string = b[b.find(CONTRACT_FILENAME):]

            # separated_list = broken_string.split(':')
            # error_desc = ' '.join([x.strip() for x in separated_list[4:]])
            return True
            # return {
            #     'success': False,
            #     'error': True,
            #     'filename': CONTRACT_FILENAME,
            #     'lineno': int(separated_list[1]),
            #     'character': int(separated_list[2]),
            #     'details': error_desc[:error_desc.index('\x1b[0m\n')].strip(),
            #     'code': error_desc[error_desc.index('\x1b[0m\n') +
            #                        len('\x1b[0m\n'):]
            # }

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
