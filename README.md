# Coinsensus

### Steps to run Coinsensus backend server:

Reference ResilientDB Blog - [Getting Started With ResVault](https://blog.resilientdb.com/2023/09/21/ResVault.html)

1. Run ResilientDB KV Service in the *incubator-resilientdb* repo with the following command:
`./service/tools/kv/server_tools/start_kv_service.sh`
2. Start the Crow HTTP Service in the *incubator-resilientdb-graphql* repo with the following command:
`bazel-bin/service/http_server/crow_service_main service/tools/config/interface/client.config service/http_server/server_config.config`
3. Within the virtual environment, start the Python SDK GraphQL Server in the *incubator-resilientdb-graphql* repo with the following command:
`python3 app.py`
4. Within the virtual environment, start the Coinsensus Backend Python FastAPI server with the following command in the *coinsensus-backend* repo:
`python3 app/main.py`

### APIs exposed:
- /api/users/createUser
- /api/users/login
- /api/users/getUser
- /api/users/addFriend
- /api/users/getFriends
- /api/transactions/createTransaction
- /api/transactions/getBalances
- /api/transactions/getTransactionHistory
