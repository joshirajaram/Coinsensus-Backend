from typing import Optional, Tuple
from models import Transaction, User
import json
import requests

def add_transaction(transaction: Transaction) -> Optional[str]:
    """Generate POST API Request to ResDB"""

    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE"
            amount: {transaction.amount},
            signerPublicKey: "{transaction.sender}",
            signerPrivateKey: "{transaction.sender_private_key}",
            recipientPublicKey: "{transaction.receiver}",
            asset: \"\"\"{json.dumps(transaction.asset)}\"\"\"
        }}) {{
                id
            }}
        }}
    """
    
    update_balances(transaction)

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200: 
        print("response : ",response.content)
        return None
    else:
        return str(response)
    
def add_user(user: User) -> Tuple[Optional[str], Optional[str]]:
    """Generate POST API Request to ResDB"""

    asset = {
        "data": {
            "method": "create_user",
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "timestamp": str(user.signup_ts),
            "name": user.name,
            "public_key": user.public_key,
            "private_key": user.private_key,
            "friends": user.friends,
            "balances": user.balances
        }
    }

    # Serialize the asset dictionary to a JSON-formatted string
    asset_json = json.dumps(asset)
    print(asset_json)

    # Construct the GraphQL mutation query
    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE",
            amount: 1,
            signerPublicKey: "{user.public_key}",
            signerPrivateKey: "{user.private_key}",
            recipientPublicKey: "{user.public_key}",
            asset: \"\"\"{json.dumps(asset)}\"\"\",
        }}) {{
            id
        }}
    }}
    """

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200: 
        print("response : ",response.content)
        res = json.loads(response.content)
        return (res["data"]["postTransaction"]["id"], None)
    else:
        return (None, str(response))

def update_balances(transaction: Transaction) -> Optional[str]:
    query = f"""
    query {{
        getFilteredTransactions(filter: {{
            ownerPublicKey: "{transaction.sender}",
            recipientPublicKey: "{transaction.sender}"
        }}) {{
            id
            asset
        }}
    }}
    """

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200:
        print("response : ",response.content)
        id = response.json()['data']['getFilteredTransactions'][0]['id']
        asset = response.json()['data']['getFilteredTransactions'][0]['asset']
        
        updated = False
        for bal in asset['data']['balances']:
            if bal['username'] == transaction.asset['data']['username']:
                bal['balance'] += transaction.asset['data']['balance']
                updated = True

        if not updated:
            asset['data']['balances'].append({
                "username": transaction.asset['data']['username'],
                "balance": transaction.asset['data']['balance']
            })
        
        query = f"""
        mutation {{
            updateTransaction(data: {{
                id: {id},
                operation: "",
                amount: {transaction.amount},
                signerPublicKey: "{transaction.sender}",
                signerPrivateKey: "{transaction.sender_private_key}",
                recipientPublicKey: "{transaction.sender}",
                asset: \"\"\"{json.dumps(asset)}\"\"\",
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