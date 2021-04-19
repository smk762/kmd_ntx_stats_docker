from django.urls import path
from kmd_ntx_api import api_wallet

api_wallet_urls = [

    # API WALLET V2
    path('api/wallet/chain_addresses/',
          api_wallet.chain_addresses_wallet,
          name='chain_addresses_wallet'),

    path('api/wallet/chain_balances/',
          api_wallet.chain_balances_wallet,
          name='chain_balances_wallet'),

    path('api/wallet/notary_addresses/',
          api_wallet.notary_addresses_wallet,
          name='notary_addresses_wallet'),

    path('api/wallet/notary_balances/',
          api_wallet.notary_balances_wallet,
          name='notary_balances_wallet'),

]