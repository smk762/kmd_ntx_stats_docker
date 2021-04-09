
# TODO: Delegate this to crons and table
def get_chain_sync_data(request):
    season = get_season()
    coins_data = get_coins_data(1).values('chain', 'dpow')
    context = {}
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        chain_sync_data = r.json()
        sync_data_keys = list(chain_sync_data.keys())
        chain_count = 0
        sync_count = 0
        for chain in sync_data_keys:
            if chain == 'last_updated':
                last_data_update = day_hr_min_sec(
                    int(time.time()) - int(chain_sync_data['last_updated'])
                )
                chain_sync_data.update({
                    "last_data_update": last_data_update
                })
            elif chain.find('last') == -1:
                chain_count += 1
                if "last_sync_blockhash" in chain_sync_data[chain]:
                    if chain_sync_data[chain]["last_sync_blockhash"] == chain_sync_data[chain]["last_sync_dexhash"]:
                        sync_count += 1
                if 'last_sync_timestamp' in chain_sync_data[chain] :
                    last_sync_update = day_hr_min_sec(
                        int(time.time()) - int(chain_sync_data[chain]['last_sync_timestamp'])
                    )
                else:
                    last_sync_update = "-"
                chain_sync_data[chain].update({
                    "last_sync_update": last_sync_update
                })
        sync_pct = round(sync_count/chain_count*100,3)
        context.update({
            "chain_sync_data":chain_sync_data,
            "sync_count":sync_count,
            "sync_pct":sync_pct,
            "chain_count":chain_count
        })
    except Exception as e:
        logger.error(f"[get_chain_sync_data] Exception: {e}")
        messages.error(request, 'Sync Node API not Responding!')
    return context