
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