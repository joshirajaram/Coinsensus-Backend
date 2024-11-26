from typing import Optional
from models import Transaction
from config import graphql_url
import json
import requests

def add_transaction(transaction: Transaction) -> Optional[str]:
    """Generate POST API Request to ResDB"""
    data = {
        "operation": "CREATE",
        "amount": transaction.amount,
        "signerPublicKey": transaction.sender,
        "signerPrivateKey": transaction.sender_private_key,
        "recipientPublicKey": transaction.receiver,
        "asset": """{
            "data": { "timestamp": %s },
        }""" % transaction.timestamp
    }
    body = "mutation { postTransaction(data: %s ) { id } }" % json.dumps(data)
    response = requests.post(url = graphql_url, json = {"query": body}) 
    print("response status code: ", response.status_code) 
    if response.status_code == 200: 
        print("response : ",response.content)
        return None
    else:
        return str(response.status_code)