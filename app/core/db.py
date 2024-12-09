from typing import Optional, Tuple, Any, List
from models import Transaction, User
import json
import requests

def add_transaction(transaction: Transaction) -> Tuple[Optional[str], Optional[str]]:
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

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200:
        print("response : ",response.content)
        res = json.loads(response.content)
        return (res["data"]["postTransaction"]["id"], None)
    else:
        return (None, str(response))
    
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
    print("*************************************************************")
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
        
def get_user_details(id: str) -> Any:
    try:
        query = f"""
        query {{
            getTransaction(id: "{id}") {{
                id
                asset
            }}
        }}
        """
        response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query})
        if response.status_code == 200:
            outer_dict = json.loads(response.content)
            asset_str = outer_dict['data']['getTransaction']['asset'].replace("'", '"')
            asset_dict = json.loads(asset_str)
            return asset_dict['data']
        else:
            return (None, str(response.status_code))
    except:
        return "Error in get_user_detail"

def add_friend(id: str, friend: str) -> Any:
    try:
        user_asset = get_user_details(id)
        
        friends_list = user_asset['friends']
        friends_list.append(friend)
        print("Friend list", friends_list)
        
        user_asset['friends'] = friends_list
        asset = {"data": user_asset}
        
        asset_json = json.dumps(asset)

        query = f"""
        mutation {{
            updateTransaction(data: {{
                id: "{id}"
                operation: ""
                amount: 1,
                signerPublicKey: "{user_asset['public_key']}",
                signerPrivateKey: "{user_asset['private_key']}",
                recipientPublicKey: "{user_asset['public_key']}",
                asset: \"\"\"{asset_json}\"\"\"
            }}) {{
                id
                asset
            }}
        }}
        """
        response = requests.post(url="http://localhost:8000/graphql", json={"query": query})
        if response.status_code == 200:
            res = json.loads(response.content)
            new_id = res['data']['updateTransaction']['id']
            return new_id
        else:
            return response.content
    except Exception as e:
        print("Error:", e)
        return f"Error occurred: {str(e)}"
    
def get_transaction_history(user_public_key: str, friends: List[str], friends_public_keys: List[str]) -> Any:
    transactions = {
        "sent": {},
        "received": {}
    }
    
    # User in sender
    for i in range(len(friends)):
        try:
            query = f"""
            query {{ getFilteredTransactions(filter: {{
                ownerPublicKey: "{user_public_key}",
                recipientPublicKey: "{friends_public_keys[i]}"
                }}) {{
                    id
                    asset
                }}
            }}
            """
            response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query})
            if response.status_code == 200:
                res = json.loads(response.content)
                for transaction in res['data']['getFilteredTransactions']:
                    if friends[i] not in transactions["sent"]:
                        transactions["sent"][friends[i]] = []
                    transactions["sent"][friends[i]].append(transaction)
                # return asset_dict['data']
            # else:
            #     return (None, str(response.status_code))
        except:
            return "Error in get_transaction_history"
    
    # User in receiver
    for i in range(len(friends)):
        try:
            query = f"""
            query {{ getFilteredTransactions(filter: {{
                ownerPublicKey: "{friends_public_keys[i]}",
                recipientPublicKey: "{user_public_key}"
                }}) {{
                    id
                    asset
                }}
            }}
            """
            response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query})
            if response.status_code == 200:
                res = json.loads(response.content)
                for transaction in res['data']['getFilteredTransactions']:
                    if friends[i] not in transactions["received"]:
                        transactions["received"][friends[i]] = []
                    transactions["received"][friends[i]].append(transaction)
                # return asset_dict['data']
            # else:
            #     return (None, str(response.status_code))
        except:
            return "Error in get_transaction_history"
    
    return transactions
