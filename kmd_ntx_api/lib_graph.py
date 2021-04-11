from kmd_ntx_api.lib_info import *


def get_balances_graph_data(request, filter_kwargs):

    if 'chain' in request.GET:
        filter_kwargs.update({'chain':request.GET['chain']})
    elif 'notary' in request.GET:
        filter_kwargs.update({'notary':request.GET['notary']})
    else:
        filter_kwargs.update({'chain':'KMD'})

    data = get_balances_data().filter(**filter_kwargs).values()
    notary_list = []                                                                          
    chain_list = []
    balances_dict = {}
    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        if item['chain'] not in chain_list:
            chain_list.append(item['chain'])
        if item['notary'] not in balances_dict:
            balances_dict.update({item['notary']:{}})
        if item['chain'] not in balances_dict[item['notary']]:
            balances_dict[item['notary']].update({item['chain']:item['balance']})
        else:
            bal = balances_dict[item['notary']][item['chain']] + item['balance']
            balances_dict[item['notary']].update({item['chain']:bal})

    chain_list.sort()
    notary_list.sort()
    notary_list = region_sort(notary_list)

    bg_color = []
    border_color = []

    season = filter_kwargs["season"]
    coins_dict = get_dpow_server_coins_dict(season)
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain+ " Notary Balances"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(RED)
            elif notary.endswith("_EU"):
                bg_color.append(LT_GREEN)
            elif notary.endswith("_NA"):
                bg_color.append(LT_PURPLE)
            elif notary.endswith("_SH"):
                bg_color.append(LT_BLUE)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)
    else:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notary Balances"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(LT_PURPLE)
            elif chain in main_chains:
                bg_color.append(LT_GREEN)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            chartdata.append(balances_dict[notary][chain])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 
    return data


def get_daily_ntx_graph_data(request, filter_kwargs):
    ntx_dict = {}
    bg_color = []
    border_color = []
    third_chains = []
    main_chains = []
    notary_list = []                                                                         
    chain_list = []
    labels = []
    chartdata = []
    filter_kwargs = {}

    if 'notarised_date' in request.GET:
        filter_kwargs.update({'notarised_date':request.GET['notarised_date']})
    else:
        today = datetime.date.today()
        filter_kwargs.update({'notarised_date':today})
    if 'notary' in request.GET:
        filter_kwargs.update({'notary':request.GET['notary']})
    elif 'chain' not in request.GET:
        filter_kwargs.update({'notary':'alien_AR'})

    data = get_notarised_count_daily_data().filter(**filter_kwargs) \
                .values('notary', 'notarised_date','chain_ntx_counts')

    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        chain_list += list(item['chain_ntx_counts'].keys())
        ntx_dict.update({item['notary']:item['chain_ntx_counts']})

    if 'chain' in request.GET:
        chain_list = [request.GET['chain']]
    else:
        chain_list = list(set(chain_list))
        chain_list.sort()

    notary_list.sort()
    notary_list = region_sort(notary_list)
    season = "Season_4"
    coins_dict = get_dpow_server_coins_dict(season)
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain+ " Notarisations"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(RED)
            elif notary.endswith("_EU"):
                bg_color.append(LT_GREEN)
            elif notary.endswith("_NA"):
                bg_color.append(LT_PURPLE)
            elif notary.endswith("_SH"):
                bg_color.append(LT_BLUE)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notarisations"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(LT_BLUE)
            elif chain in main_chains:
                bg_color.append(LT_GREEN)
            else:
                bg_color.append(LT_PURPLE)
            border_color.append(BLACK)

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            if chain in ntx_dict[notary]:
                chartdata.append(ntx_dict[notary][chain])
            else:
                chartdata.append(0)
    

    data = { 
        "labels":labels, 
        "chartLabel":chartdata, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    }
    return data


# TODO: This function not used?
def get_notary_balances_graph(notary, season=None):
    if not season:
        season = "Season_4"

    notary_balances = get_notary_balances(notary, season)
    main_chains, third_chains = get_server_chains_lists(season)

    balances_graph_dict = {}
    notary_balances_list = []
    for item in notary_balances:

        if item['node'] == 'third party' and item['chain'] == "KMD":
            chain = "KMD_3P"

        else: 
            chain = item['chain']

        if chain in main_chains and item["node"] == 'main':
            notary_balances_list.append(item)
            balances_graph_dict.update({chain:float(item['balance'])})

        elif item["node"] == 'third party' and chain in third_chains or chain == "KMD_3P":
            balances_graph_dict.update({chain:float(item['balance'])})
            notary_balances_list.append(item)


    labels = list(main_chains+third_chains)

    bg_color = []
    border_color = []
    for label in labels:
        border_color.append(BLACK)

        if label in ['KMD', 'KMD_3P', 'BTC']:
            bg_color.append(LT_ORANGE)

        elif label in third_chains:
            bg_color.append(LT_PURPLE)

        elif label in main_chains:
            bg_color.append(LT_GREEN)

    chartdata = []
    for label in labels:
        if label in balances_graph_dict:
            chartdata.append(balances_graph_dict[label])

    notary_balances_graph = { 
        "labels":labels, 
        "chartLabel":f"BALANCES",
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 

    return notary_balances_list, notary_balances_graph