from django.urls import path
from kmd_ntx_api import wallet_api

api_wallet_urls = [

    # API WALLET V2
    path('api/wallet/coin_addresses/',
          wallet_api.coin_addresses_wallet,
          name='coin_addresses_wallet'),

    path('api/wallet/coin_balances/',
          wallet_api.coin_balances_wallet,
          name='coin_balances_wallet'),

    path('api/wallet/notary_addresses/',
          wallet_api.notary_addresses_wallet,
          name='notary_addresses_wallet'),

    path('api/wallet/notary_balances/',
          wallet_api.notary_balances_wallet,
          name='notary_balances_wallet'),

]
