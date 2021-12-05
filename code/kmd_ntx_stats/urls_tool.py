from django.urls import path
from kmd_ntx_api import views_tool
from kmd_ntx_api import api_tools

# TOOL VIEWS
frontend_tool_urls = [


    path('tools/convert_addresses/',
          views_tool.convert_addresses_view,
          name='convert_addresses_view'),

    path('tools/create_raw_transaction/',
          views_tool.create_raw_transaction_view,
          name='create_raw_transaction_view'),

    path('tools/daemon_clis/',
          views_tool.daemon_cli_view,
          name='daemon_cli_view'),

    path('tools/decode_opret/',
          views_tool.decode_opret_view,
          name='decode_opret_view'),

    path('tools/kmd_rewards/',
          views_tool.kmd_rewards_view,
          name='kmd_rewards_view'),

    path('tools/launch_params/',
          views_tool.launch_params_view,
          name='launch_params_view'),

    path('tools/pubkey_addresses/',
          views_tool.pubkey_addresses_view,
          name='pubkey_addresses_view'),

    path('tools/scripthashes_from_pubkey/',
          views_tool.scripthashes_from_pubkey_view,
          name='scripthashes_from_pubkey_view'),

    path('tools/scripthash_from_address/',
          views_tool.scripthash_from_address_view,
          name='scripthash_from_address_view'),

    path('tools/send_raw_tx/',
          views_tool.send_raw_tx_view,
          name='send_raw_tx_view'),
]


# API TOOLS V2
api_tool_urls = [

    path('api/tools/addr_from_base58/',
          views_tool.addr_from_base58_tool,
          name='addr_from_base58_tool'),

    path('api/tools/address_conversion/',
          views_tool.address_conversion_tool,
          name='address_conversion_tool'),

    path('api/tools/address_from_pubkey/',
          views_tool.address_from_pubkey_tool,
          name='address_from_pubkey_tool'),

    path('api/tools/decode_opreturn/',
          api_tools.decode_op_return_tool,
          name='decode_op_return_tool'),

    path('api/tools/kmd_rewards/',
          api_tools.get_kmd_rewards,
          name='get_kmd_rewards'),

    path('api/tools/notary_utxos/',
          api_tools.get_notary_utxo_count,
          name='get_notary_utxo_count'),

    path('api/tools/scripthash_from_address/',
          api_tools.scripthash_from_address_tool,
          name='scripthash_from_address_tool'),

    path('api/tools/scripthashes_from_pubkey/',
          api_tools.scripthashes_from_pubkey_tool,
          name='scripthashes_from_pubkey_tool'),

    path('api/tools/send_raw_tx/',
          api_tools.send_raw_tx_tool,
          name='send_raw_tx_tool'),
    
]