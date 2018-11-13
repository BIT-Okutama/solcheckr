import json
import os
import subprocess

CONTRACT_FILENAME = 'tempContract.sol'


def analyze_contract(contract=None):
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

        return audit_report

    return None
