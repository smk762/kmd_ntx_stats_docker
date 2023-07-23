from django.urls import path
from kmd_ntx_api import tools_views
from kmd_ntx_api import tools_api

# TOOL VIEWS
frontend_tool_urls = [


    path('tools/convert_addresses/',
          tools_views.convert_addresses_view,
          name='convert_addresses_view'),

    path('tools/create_raw_transaction/',
          tools_views.create_raw_transaction_view,
          name='create_raw_transaction_view'),

    path('tools/daemon_clis/',
          tools_views.daemon_cli_view,
          name='daemon_cli_view'),

    path('tools/decode_opreturn/',
          tools_views.decode_op_return_view,
          name='decode_op_return_view'),

    path('tools/faucet/',
          tools_views.faucet_view,
          name='faucet_view'),
    
    path('tools/explorer_status/',
          tools_views.explorer_status_view,
          name='explorer_status_view'),

    path('tools/launch_params/',
          tools_views.launch_params_view,
          name='launch_params_view'),

    path('tools/pubkey_addresses/',
          tools_views.pubkey_addresses_view,
          name='pubkey_addresses_view'),

    path('tools/scripthashes_from_pubkey/',
          tools_views.scripthashes_from_pubkey_view,
          name='scripthashes_from_pubkey_view'),

    path('tools/scripthash_from_address/',
          tools_views.scripthash_from_address_view,
          name='scripthash_from_address_view'),

    path('tools/send_raw_tx/',
          tools_views.send_raw_tx_view,
          name='send_raw_tx_view'),
]


# API TOOLS V2
api_tool_urls = [

    path('api/tools/addr_from_base58/',
          tools_api.addr_from_base58_tool,
          name='addr_from_base58_tool'),

    path('api/tools/address_conversion/',
          tools_api.address_conversion_tool,
          name='address_conversion_tool'),

    path('api/tools/address_from_pubkey/',
          tools_api.address_from_pubkey_tool,
          name='address_from_pubkey_tool'),

    path('api/tools/decode_opreturn/',
          tools_api.decode_op_return_tool,
          name='decode_op_return_tool'),

    path('api/tools/pubkey_utxos/',
          tools_api.pubkey_utxos_tool,
          name='pubkey_utxos_tool'),

    path('api/tools/explorer_status/',
          tools_api.explorer_status_tool,
          name='explorer_status_tool'),

    path('api/tools/send_raw_tx/',
          tools_api.send_raw_tx_tool,
          name='send_raw_tx_tool'),

    path('api/tools/scripthash_from_address/',
          tools_api.scripthash_from_address_tool,
          name='scripthash_from_address_tool'),

    path('api/tools/scripthashes_from_pubkey/',
          tools_api.scripthashes_from_pubkey_tool,
          name='scripthashes_from_pubkey_tool'),

]