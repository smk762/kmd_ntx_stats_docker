from kmd_ntx_api.lib_info import *


def get_balances_graph_data(request):
    season = None
    server = None
    chain = None
    notary = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
        if server in ["KMD", "LTC", "BTC"]:
            server = "Main"
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "notary" in request.GET:
        notary = request.GET["notary"]

    if not season or not server or (not chain and not notary):
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'server'] and at least one of the following ['notary', 'chain']"
        }

    data = get_balances_data(season, server, chain, notary).values()
    notary_list = []
    chain_list = []
    balances_dict = {}
    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        if item['chain'] not in chain_list:
            chain_list.append(item['chain'])
        if item['notary'] not in balances_dict:
            balances_dict.update({item['notary']: {}})
        if item['chain'] not in balances_dict[item['notary']]:
            balances_dict[item['notary']].update(
                {item['chain']: item['balance']})
        else:
            bal = balances_dict[item['notary']
                                ][item['chain']] + item['balance']
            balances_dict[item['notary']].update({item['chain']: bal})

    chain_list.sort()
    notary_list.sort()
    notary_list = region_sort(notary_list)

    bg_color = []
    border_color = []

    coins_dict = get_dpow_server_coins_dict(season)
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain + " Notary Balances"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(AR_REGION)
            elif notary.endswith("_EU"):
                bg_color.append(EU_REGION)
            elif notary.endswith("_NA"):
                bg_color.append(NA_REGION)
            elif notary.endswith("_SH"):
                bg_color.append(SH_REGION)
            else:
                bg_color.append(DEV_REGION)
            border_color.append(BLACK)
    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary + " Notary Balances"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(THIRD_PARTY_COLOR)
            elif chain in main_chains:
                bg_color.append(MAIN_COLOR)
            else:
                bg_color.append(OTHER_COIN_COLOR)
            border_color.append(BLACK)
    else:
        return {
            "labels": [],
            "chartLabel": "",
            "chartdata": [],
            "bg_color": [],
            "border_color": [],
        }

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            chartdata.append(balances_dict[notary][chain])

    return {
        "labels": labels,
        "chartLabel": chartLabel,
        "chartdata": chartdata,
        "bg_color": bg_color,
        "border_color": border_color,
    }


def get_daily_ntx_graph_data(request):
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

    notarised_date = None
    season = None
    chain = None
    notary = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notarised_date" in request.GET:
        notarised_date = request.GET["notarised_date"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "notary" in request.GET:
        notary = request.GET["notary"]

    if not notarised_date or not season or (not chain and not notary):
        return {
            "error": "You need to specify both of the following filter parameters: ['notarised_date', 'season'] and at least one of the following ['notary', 'chain']"
        }

    coins_dict = get_dpow_server_coins_dict(season)
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    data = get_notarised_count_daily_data(notarised_date, notary)
    data = data.values('notary', 'notarised_date', 'chain_ntx_counts')

    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        chain_list += list(item['chain_ntx_counts'].keys())
        ntx_dict.update({item['notary']: item['chain_ntx_counts']})

    if 'chain' in request.GET:
        chain_list = [request.GET['chain']]
    else:
        chain_list = list(set(chain_list))
        chain_list.sort()

    notary_list.sort()
    notary_list = region_sort(notary_list)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain + " Notarisations"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(RED)
            elif notary.endswith("_EU"):
                bg_color.append(MAIN_COLOR)
            elif notary.endswith("_NA"):
                bg_color.append(THIRD_PARTY_COLOR)
            elif notary.endswith("_SH"):
                bg_color.append(LT_BLUE)
            else:
                bg_color.append(OTHER_COIN_COLOR)
            border_color.append(BLACK)

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary + " Notarisations"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(LT_BLUE)
            elif chain in main_chains:
                bg_color.append(MAIN_COLOR)
            else:
                bg_color.append(THIRD_PARTY_COLOR)
            border_color.append(BLACK)

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            if chain in ntx_dict[notary]:
                chartdata.append(ntx_dict[notary][chain])
            else:
                chartdata.append(0)

    return {
        "labels": labels,
        "chartLabel": chartLabel,
        "chartdata": chartdata,
        "bg_color": bg_color,
        "border_color": border_color,
    }


# TODO: Deprecate later (used in notary_profile_view)
def get_notary_balances_graph(notary, season=None):
    if not season:
        season = SEASON

    notary_balances = get_notary_balances(notary, season)
    main_chains, third_chains = get_dpow_server_coins_dict_lists(season)

    for chain in RETIRED_CHAINS:
        if chain in third_chains:
            third_chains.remove(chain)

    main_chains += ["KMD", "BTC", "LTC"]
    main_chains.sort()
    balances_graph_dict = {}
    notary_balances_list = []
    for item in notary_balances:

        chain = item['chain']
        if item['server'] == 'Third_Party':
            if item['chain'] == "KMD":
                chain = "KMD_3P"
        if item['server'] in ["LTC", "BTC", "KMD"]:
            item.update({"server": "Main"})

        if chain in main_chains and item["server"] == 'Main':
            notary_balances_list.append(item)
            balances_graph_dict.update({chain: float(item['balance'])})

        elif item["server"] == 'Third_Party' and chain in third_chains or chain == "KMD_3P":
            balances_graph_dict.update({chain: float(item['balance'])})
            notary_balances_list.append(item)

    labels = list(main_chains+third_chains)

    bg_color = []
    border_color = []
    for label in labels:
        border_color.append(BLACK)

        if label in ['KMD', 'KMD_3P', 'BTC', 'LTC']:
            bg_color.append(OTHER_COIN_COLOR)

        elif label in third_chains:
            bg_color.append(THIRD_PARTY_COLOR)

        elif label in main_chains:
            bg_color.append(MAIN_COLOR)

    chartdata = []
    for label in labels:
        if label in balances_graph_dict:
            chartdata.append(balances_graph_dict[label])

    notary_balances_graph = {
        "labels": labels,
        "chartLabel": f"BALANCES",
        "chartdata": chartdata,
        "bg_color": bg_color,
        "border_color": border_color,
    }

    return notary_balances_list, notary_balances_graph
