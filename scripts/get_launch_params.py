import requests

r = requests.get('http://notary.earth:8762/info/coins/?dpow_active=1')

coins = r.json()['results'][0]
for coin in coins:
    print(coin)
    print(coins[coin]['dpow']['launch_params'])
    print(coins[coin]['dpow']['conf_path'])
    print(coins[coin]['dpow']['cli'])
