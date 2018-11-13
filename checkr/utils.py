import json
import os
import subprocess

CONTRACT_FILENAME = 'contract.sol'


def analyze_contract(contract):
    if contract:
        # temporarily write a .sol file for Mythril to check
        # TODO: Find better approach
        with open(CONTRACT_FILENAME, 'w') as f:
            f.write(contract)

        # use Mythril through subprocess
        terminal_audit = subprocess.run(
            ["myth", "-xo", "json", CONTRACT_FILENAME],
            stdout=subprocess.PIPE
        )
        audit_report = json.loads(terminal_audit.stdout.strip())

        if os.path.exists(CONTRACT_FILENAME):
            os.remove(CONTRACT_FILENAME)

        if not audit_report.get('success') and audit_report.get('error'):
            message = audit_report.get('error')

            # ex. '8:21: Error: Expected primary expression.'
            broken_string = message[message.index(CONTRACT_FILENAME) +
                                    len(CONTRACT_FILENAME) + 1:]
            separated_list = broken_string.split(':')

            return {
                'success': False,
                'error': True,
                'line': int(separated_list[0]),
                'character': int(separated_list[1]),
                'details': ' '.join([x.strip() for x in separated_list[3:]])
            }

        return audit_report

    return None
