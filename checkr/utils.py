import ast
import os
import subprocess

CONTRACT_FILENAME = 'contract.sol'
REPORT_FILENAME = 'report.json'


def analyze_contract(contract):
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
            'filename': CONTRACT_FILENAME,
            'issues': json_report
        }

    return None
