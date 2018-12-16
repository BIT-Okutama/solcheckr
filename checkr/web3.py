import time

from decouple import config
from web3 import Web3, HTTPProvider

from checkr import contract_abi

CONTRACT_ADDRESS = config('CONTRACT_ADDRESS')
WALLET_PRIVATE_KEY = config('WALLET_PRIVATE_KEY')
WALLET_ADDRESS = config('WALLET_ADDRESS')


def broadcast_audit_result(tracking, result=None):
    if tracking and result is not None:
        w3 = Web3(HTTPProvider(config('INFURA_URL')))
        w3.eth.enable_unaudited_features()
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi.abi)

        nonce = w3.eth.getTransactionCount(WALLET_ADDRESS)

        txn_dict = contract.functions.setAuditResult(tracking, result).buildTransaction({
            'chainId': 3,
            'gas': 140000,
            'gasPrice': w3.toWei('40', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=WALLET_PRIVATE_KEY)

        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_receipt = w3.eth.getTransactionReceipt(result)

        count = 0
        while tx_receipt is None and (count < 30):
            time.sleep(10)
            tx_receipt = w3.eth.getTransactionReceipt(result)
            print(tx_receipt)

        if tx_receipt is None:
            return {'status': 'failed', 'error': 'timeout'}

        processed_receipt = contract.events.ResultSet().processReceipt(tx_receipt)

        print(processed_receipt)

        return {'status': 'success', 'processed_receipt': processed_receipt}
    return False
