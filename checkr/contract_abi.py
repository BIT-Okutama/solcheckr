abi = """[
    {
        "constant": true,
        "inputs": [
            {
                "name": "",
                "type": "bytes32"
            }
        ],
        "name": "auditResults",
        "outputs": [
            {
                "name": "isSet",
                "type": "bool"
            },
            {
                "name": "isSafe",
                "type": "bool"
            },
            {
                "name": "auditType",
                "type": "uint8"
            },
            {
                "name": "author",
                "type": "address"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_auditType",
                "type": "uint8"
            }
        ],
        "name": "addAudit",
        "outputs": [
            {
                "name": "",
                "type": "bytes32"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "name": "",
                "type": "address"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_auditTracker",
                "type": "bytes32"
            }
        ],
        "name": "viewResult",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            },
            {
                "name": "",
                "type": "uint8"
            },
            {
                "name": "",
                "type": "address"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_auditTracker",
                "type": "bytes32"
            },
            {
                "name": "_result",
                "type": "bool"
            }
        ],
        "name": "setAuditResult",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "transferOwnership",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": false,
                "name": "author",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "auditType",
                "type": "uint8"
            },
            {
                "indexed": false,
                "name": "tracker",
                "type": "bytes32"
            }
        ],
        "name": "AuditAdded",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": false,
                "name": "tracker",
                "type": "bytes32"
            },
            {
                "indexed": false,
                "name": "result",
                "type": "bool"
            }
        ],
        "name": "ResultSet",
        "type": "event"
    }
]"""
