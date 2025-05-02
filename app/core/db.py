import os
from typing import Optional, Tuple, Any, List
from models import Transaction, User
import json
import requests

from core import config

def dict_to_graphql_input(obj):
    if isinstance(obj, dict):
        fields = []
        for k, v in obj.items():
            fields.append(f"{k}: {dict_to_graphql_input(v)}")
        return "{" + ", ".join(fields) + "}"
    elif isinstance(obj, list):
        return "[" + ", ".join(dict_to_graphql_input(i) for i in obj) + "]"
    elif isinstance(obj, str):
        return f"\"{v_escape(obj)}\""
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif obj is None:
        return "null"
    else:
        return str(obj)

def v_escape(s):
    return s.replace('"', '\\"')  # escape any inner double quotes

def add_transaction(transaction: Transaction) -> Tuple[Optional[str], Optional[str]]:
    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE"
            amount: {transaction.amount},
            signerPublicKey: "{transaction.sender}",
            signerPrivateKey: "{transaction.sender_private_key}",
            recipientPublicKey: "{transaction.receiver}",
            asset: {dict_to_graphql_input(transaction.asset)}
        }}) {{
                id
            }}
        }}
    """

    response = requests.post(url = os.getenv('GRAPHQL_URL', config.GRAPHQL_URL), json = {"query": query})
    print("response status code: ", response.status_code)
    if response.status_code == 200:
        print("response : ",response.content)
        res = json.loads(response.content)
        return (res["data"]["postTransaction"]["id"], None)
    else:
        return (None, str(response))
    
def add_user(user: User) -> Tuple[Optional[str], Optional[str]]:
    """Generate POST API Request to ResDB"""

    asset = f"""{{
        data: {{
            method: "create_user"
            id: "{user.id}"
            username: "{user.username}"
            password: "{user.password}"
            timestamp: "{str(user.signup_ts)}"
            name: "{user.name}"
            public_key: "{user.public_key}"
            private_key: "{user.private_key}"
            friends: {user.friends}
            balances: {user.balances}
        }}
    }}"""

    # Serialize the asset dictionary to a JSON-formatted string
    # asset_json = json.dumps(asset)
    print(asset)
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
            asset: {asset},
        }}) {{
            id
        }}
    }}
    """
    print("QUERY", query)
    print("*************************************************************")
    response = requests.post(url = os.getenv('GRAPHQL_URL', config.GRAPHQL_URL), json = {"query": query}) 
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
        response = requests.post(url = os.getenv('GRAPHQL_URL', config.GRAPHQL_URL), json = {"query": query})
        if response.status_code == 200:
            outer_dict = json.loads(response.content)
            print("Outer dict", outer_dict)
            asset_dict = outer_dict['data']['getTransaction']['asset']
            print("Asset", asset_dict)
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
        
        print("Asset", asset)
        asset_graphql = dict_to_graphql_input(asset)
        # Construct the GraphQL mutation query
        query = f"""
        mutation {{
            postTransaction(data: {{
                operation: "CREATE",
                amount: 1,
                signerPublicKey: "{user_asset['public_key']}"
                signerPrivateKey: "{user_asset['private_key']}"
                recipientPublicKey: "{user_asset['public_key']}"
                asset: {asset_graphql}
            }}) {{
                id
            }}
        }}
        """
        
        print("update query: ", query)
        response = requests.post(url=os.getenv('GRAPHQL_URL', config.GRAPHQL_URL), json={"query": query})
        print("response status code: ", response.status_code)
        print("response : ", response.content)
        if response.status_code == 200:
            res = json.loads(response.content)
            new_id = res['data']['postTransaction']['id']
            return new_id
        else:
            return response.content
    except Exception as e:
        print("Error:", e)
        return f"Error occurred: {str(e)}"
