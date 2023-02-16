from django.urls import path
from kmd_ntx_api import api_wallet

api_wallet_urls = [

    # API WALLET V2
    path('api/wallet/coin_addresses/',
          api_wallet.coin_addresses_wallet,
          name='coin_addresses_wallet'),

    path('api/wallet/coin_balances/',
          api_wallet.coin_balances_wallet,
          name='coin_balances_wallet'),

    path('api/wallet/notary_addresses/',
          api_wallet.notary_addresses_wallet,
          name='notary_addresses_wallet'),

    path('api/wallet/notary_balances/',
          api_wallet.notary_balances_wallet,
          name='notary_balances_wallet'),

    path('api/wallet/rewards_txids/',
          api_wallet.rewards_txids_wallet,
          name='rewards_txids_wallet')
]