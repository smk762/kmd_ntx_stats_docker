

def get_btc_ntxids(stop_block, exit=None):
    has_more=True
    before_block=None
    ntx_txids = []
    page = 1
    exit_loop = False
    existing_txids = get_existing_notarised_txids("BTC")
    while has_more:
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_btc_address_txids(BTC_NTX_ADDR, before_block)
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > API_PAGE_BREAK:
            break
        if "error" in resp:
            exit_loop = api_sleep_or_exit(resp, exit )
        else:
            page += 1
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                for tx in tx_list:
                    if tx['tx_hash'] not in ntx_txids and tx['tx_hash'] not in existing_txids:
                        ntx_txids.append(tx['tx_hash'])
                logger.info(str(len(ntx_txids))+" txids scanned...")

            if 'hasMore' in resp:
                has_more = resp['hasMore']
                if has_more:
                    before_block = tx_list[-1]['block_height']
                    if before_block < stop_block:
                        logger.info("Scanned to start of s4")
                        exit_loop = True
                    time.sleep(1)
                else:
                    logger.info("No more!")
                    exit_loop = True

            else:
                logger.info("No more tx to scan!")
                exit_loop = True
                
        if exit_loop or page >= API_PAGE_BREAK:
            logger.info("exiting address txid loop!")
            break
    ntx_txids = list(set((ntx_txids)))
    return ntx_txids
def categorize_import_transactions(notary_address, season):

    logger.info(f">>> Categorising {notary_address} for {season}")
    new_txids = get_new_notary_txids(notary_address)
    logger.info(f"Processing ETA: {0.02*len(new_txids)} sec")
    i = 1
    j = 1
    for txid in new_txids:
        txid_data = tx_row()
        txid_data.txid = txid

        # import NTX if existing on other server
        url = f"{OTHER_SERVER}/api/info/nn_btc_txid?txid={txid}"
        r = requests.get(url)
        time.sleep(0.02)
        try:
            resp = r.json()
            if resp['count'] > 0:

                # Detect NTX season
                tx_addresses = []
                for item in resp['results'][0]:
                    txid_data.block_hash = item["block_hash"]
                    txid_data.block_height = item["block_height"]
                    txid_data.block_time = item["block_time"]
                    txid_data.block_datetime = item["block_datetime"]
                    txid_data.num_inputs = item["num_inputs"]
                    txid_data.num_outputs = item["num_outputs"]
                    txid_data.fees = item["fees"]

                    if item["address"] != BTC_NTX_ADDR:
                        tx_addresses.append(item["address"])
                tx_addresses = list(set(tx_addresses))

                txid_data.season = get_season_from_btc_addresses(tx_addresses, resp['results'][0][0]["block_time"])

                tx_vins, tx_vouts = get_nn_btc_tx_parts(txid)
                txid_data.category = get_category_from_vins_vouts(tx_vins, tx_vouts, txid_data.season)

                for vin in tx_vins:
                    txid_data.address = vin["address"]
                    txid_data.notary = get_notary_from_btc_address(vin["address"], txid_data.season, vin["notary"])
                    txid_data.address = vin["address"]
                    txid_data.input_index = vin["input_index"]
                    txid_data.input_sats = vin["input_sats"]
                    txid_data.output_index = vin["output_index"]
                    txid_data.output_sats = vin["output_sats"]
                    txid_data.update()

                for vout in tx_vouts:
                    txid_data.address = vout["address"]
                    txid_data.notary = get_notary_from_btc_address(vout["address"], txid_data.season, vout["notary"])                    
                    txid_data.address = vout["address"]
                    txid_data.input_index = vout["input_index"]
                    txid_data.input_sats = vout["input_sats"]
                    txid_data.output_index = vout["output_index"]
                    txid_data.output_sats = vout["output_sats"]
                    txid_data.update()

        except Exception as e:
            logger.error(e)
            logger.error(r.text)
            
        
        j += 1
    i += 1


def get_notarisations(season=None, chain=None, scored=None):
    txids = []
    logger.info("Getting existing NTXIDs from database...")
    sql = f"SELECT txid, block_time, chain, season, scored from notarised"
    filters = []
    if season:
        filters.append(f"season='{season}'")
    if chain:
        filters.append(f"chain='{chain}'")
    if scored:
        filters.append(f"scored='{scored}'")
    if len(filters) > 0:
        sql += " WHERE "+" AND ".join(filters)
    sql += ";"
    CURSOR.execute(sql)
    resp = CURSOR.fetchall()

    for item in resp:
        txids.append({
            "txid":item[0],
            "block_time":item[1],
            "chain":item[2],
            "season":item[3],
            "scored":item[4]
        })
    return txids