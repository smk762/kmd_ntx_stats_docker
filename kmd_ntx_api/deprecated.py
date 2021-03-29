
# No longer used
def get_nn_health():
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    if 1 == 0:
        coins_data = coins.objects.filter(dpow_active=1).values('chain')
        chains_list = []
        for item in coins_data:
            # ignore BTC, OP RETURN lists ntx to BTC as "KMD"
            if item['chain'] not in chains_list and item['chain'] != 'BTC':
                chains_list.append(item['chain'])

        sync_matches = []
        sync_mismatches = []
        sync_no_exp = []
        sync_no_sync = []
        sync = chain_sync.objects.all().values()
        for item in sync:
            if item['sync_hash'] == item['explorer_hash']:
                sync_matches.append(item['chain'])
            else:
                if item['explorer_hash'] != 'no exp data' and item['sync_hash'] != 'no sync data':
                    sync_mismatches.append(item['chain'])
                if item['sync_hash'] == 'no sync data':
                    sync_no_sync.append(item['chain'])
                if item['explorer_hash'] == 'no exp data':
                    sync_no_exp.append(item['chain'])    
        sync_count = len(sync_matches)
        no_sync_count = len(sync_mismatches)
        sync_pct = round(sync_count/(len(sync))*100,2)

        sync_tooltip = "<h4 class='kmd_teal'>"+str(sync_count)+"/"+str(len(sync))+" ("+str(sync_pct)+"%) recent sync hashes matching</h4>\n"
        if len(sync_mismatches) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_mismatches)+" have mismatched hashes </h5>\n"
        if len(sync_no_sync) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_no_sync)+" are not syncing </h5>\n"
        if len(sync_no_exp) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_no_exp)+" have no explorer </h5>\n"

        season = get_season()
        notary_list = get_notary_list(season)

        timenow = int(time.time())
        day_ago = timenow-60*60*24

        filter_kwargs = {
            'block_time__gte':day_ago,
            'block_time__lte':timenow
        }

        ntx_data = notarised.objects.filter(**filter_kwargs)
        ntx_chain_24hr = ntx_data.values('chain') \
                         .annotate(max_ntx_time=Max('block_time'))

        ntx_chains = []
        for item in ntx_chain_24hr:
            ntx_chains.append(item['chain'])
        ntx_chains = list(set(ntx_chains))

        ntx_node_24hr = ntx_data.values('notaries')
        ntx_nodes = []
        for item in ntx_node_24hr:
            ntx_nodes += item['notaries']
        ntx_nodes = list(set(ntx_nodes))

        mining_data = mined.objects.filter(**filter_kwargs) \
                     .values('name') \
                     .annotate(num_mined=Count('name'))
        mining_nodes = []
        for item in mining_data:
            if item['name'] in notary_list:
                mining_nodes.append(item['name'])

        season = get_season()
        filter_kwargs = {'season':season}
        balances_dict = get_balances_dict(filter_kwargs) 

        # some chains do not have a working electrum, so balances ignored
        ignore_chains = ['K64', 'PGT', 'GIN']
        low_balances = get_low_balances(notary_list, balances_dict, ignore_chains)
        low_balances_dict = low_balances[0]
        low_balance_count = low_balances[1]
        sufficient_balance_count = low_balances[2]
        low_balances_tooltip = get_low_balance_tooltip(low_balances, ignore_chains)
        low_balances_pct = round(sufficient_balance_count/(low_balance_count+sufficient_balance_count)*100,2)

        non_mining_nodes = list(set(notary_list)- set(mining_nodes))
        non_ntx_nodes = list(set(notary_list).symmetric_difference(set(ntx_nodes)))
        non_ntx_chains = list(set(chains_list).symmetric_difference(set(ntx_chains)))
        mining_nodes_pct = round(len(mining_nodes)/len(notary_list)*100,2)
        ntx_nodes_pct = round(len(ntx_nodes)/len(notary_list)*100,2)
        ntx_chains_pct = round(len(ntx_chains)/len(chains_list)*100,2)


        mining_tooltip = "<h4 class='kmd_teal'>"+str(len(mining_nodes))+"/"+str(len(non_mining_nodes)+len(mining_nodes))+" ("+str(mining_nodes_pct)+"%) mined 1+ block in last 24hrs</h4>\n"
        mining_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_mining_nodes)+" are not mining! </h5>\n"

        ntx_nodes_tooltip = "<h4 class='kmd_teal'>"+str(len(ntx_nodes))+"/"+str(len(non_ntx_nodes)+len(ntx_nodes))+" ("+str(ntx_nodes_pct)+"%) notarised 1+ times in last 24hrs</h4>\n"
        ntx_nodes_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_ntx_nodes)+" are not notarising! </h5>\n"

        ntx_chains_tooltip = "<h4 class='kmd_teal'>"+str(len(ntx_chains))+"/"+str(len(non_ntx_chains)+len(ntx_chains))+" ("+str(ntx_chains_pct)+"%) notarised 1+ times in last 24hrs</h4>\n"
        ntx_chains_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_ntx_chains)+" are not notarising! </h5>\n"

        regions_info = get_regions_info(notary_list)
        sync_no_exp = []
        sync_no_sync = []
        nn_health = {
            "sync_pct":sync_pct,
            "regions_info":regions_info,
            "sync_tooltip":sync_tooltip,
            "low_balances_dict":low_balances_dict,
            "low_balances_tooltip":low_balances_tooltip,
            "low_balance_count":low_balance_count,
            "sufficient_balance_count":sufficient_balance_count,
            "balance_pct":low_balances_pct,
            "non_mining_nodes":non_mining_nodes,
            "mining_nodes":mining_nodes,
            "mining_tooltip":mining_tooltip,
            "non_mining_nodes":non_mining_nodes,
            "mining_nodes_pct":mining_nodes_pct,
            "ntx_nodes":ntx_nodes,
            "non_ntx_nodes":non_ntx_nodes,
            "ntx_nodes_pct":ntx_nodes_pct,
            "ntx_chains_tooltip":ntx_chains_tooltip,
            "chains_list":chains_list,
            "ntx_chains":ntx_chains,
            "non_ntx_chains":non_ntx_chains,
            "ntx_chains_pct":ntx_chains_pct,
            "ntx_nodes_tooltip":ntx_nodes_tooltip
        }
        return nn_health
    else:
        return {}



# Response too large
def get_mined_data(request):
    resp = {}
    data = mined.objects.all()
    data = apply_filters(request, MinedSerializer, data)
    if len(data) == len(mined.objects.all()):
        yesterday = int(time.time() -60*60*24)
        data = mined.objects.filter(block_time__gte=yesterday) \
            .order_by('season','name', 'block_height') \
            .values()
    for item in data:
        name = item['name']
        address = item['address']
        #ignore unknown addresses
        if name != address:
            season = item['season']
            block_height = item['block_height']
            if season not in resp:
                resp.update({season:{}})
            if name not in resp[season]:
                resp[season].update({name:{}})
            resp[season][name].update({
                block_height:{
                    "block_time":item['block_time'],
                    "block_datetime":item['block_datetime'],
                    "value":item['value'],
                    "address":address,
                    "txid":item['txid']
                }
            })

    return wrap_api(resp)

# Response too large
class mined_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. 
    Use filters or be patient, this is a big dataset.
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_data(request)
        return Response(api_resp)

# Response too large
class notarised_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_notarised_data(request)
        return Response(api_resp)
        
# Response too large
def get_notarised_data(request):
    resp = {}
    data = notarised.objects.all()
    data = apply_filters(request, NotarisedSerializer, data)
    if len(data) == len(notarised.objects.all()):
        yesterday = int(time.time()-60*60*24)
        data = notarised.objects.filter(block_time__gte=yesterday) \
            .order_by('season', 'chain', '-block_height') \
            .values()

    for item in data:
        txid = item['txid']
        chain = item['chain']
        block_hash = item['block_hash']
        block_time = item['block_time']
        block_datetime = item['block_datetime']
        block_height = item['block_height']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        season = item['season']
        opret = item['opret']

        if season not in resp:
            resp.update({season:{}})

        if chain not in resp[season]:
            resp[season].update({chain:{}})

        resp[season][chain].update({
            block_height:{
                "block_hash":block_hash,
                "block_time":block_time,
                "block_datetime":block_datetime,
                "txid":txid,
                "ac_ntx_blockhash":ac_ntx_blockhash,
                "ac_ntx_height":ac_ntx_height,
                "opret":opret
            }
        })

    return wrap_api(resp)