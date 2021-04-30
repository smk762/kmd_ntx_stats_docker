from django.urls import path
from kmd_ntx_api import api_status


# API STATUS V2
api_status_urls = [

    path('api/status/faucet_balance/',
          api_status.faucet_balance_status,
          name='faucet_balance_status'),

    path('api/status/faucet_pending_tx/',
          api_status.faucet_pending_tx_status,
          name='faucet_pending_tx_status'),

    path('api/status/faucet_db/',
          api_status.faucet_show_db_status,
          name='faucet_show_db_status'),

    path('api/status/faucet_address_payments/',
          api_status.faucet_address_payments_status,
          name='faucet_address_payments_status'),

]