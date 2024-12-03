from typing import Optional
from models import Transaction
import json
import requests

def add_transaction(transaction: Transaction) -> Optional[str]:
    """Generate POST API Request to ResDB"""

    asset = {
        "data": { 
            "method": "add_expense",
            "paid_by": "john_doe",
            "owed_by": ["jane_doe"],
            "timestamp": str(transaction.timestamp)
        }
    }

    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE"
            amount: {transaction.amount},
            signerPublicKey: "{transaction.sender}",
            signerPrivateKey: "{transaction.sender_private_key}",
            recipientPublicKey: "{transaction.receiver}",
            asset: \"\"\"{json.dumps(asset)}\"\"\"
        }}) {{
            id
            }}
        }}
    """

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200: 
        print("response : ",response.content)
        return None
    else:
        return str(response)