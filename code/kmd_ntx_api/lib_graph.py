from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query


def get_balances_graph_data(request):

    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if not season or (not notary and not chain):
        return {
            "error": "You need to specify the following \
                      filter parameter: ['season'] and either of ['notary', 'chain']"
        }

    data = query.get_balances_data(season, server, chain, notary).values()
    if server in ["KMD", "LTC", "BTC"]:
        server = "Main"

    chartLabel = ""
    bg_color = []
    chartdata = []
    chain_list = []
    notary_list = []
    border_color = []
    balances_dict = {}

    for item in data:
        helper.append_unique(notary_list, item['notary'])
        helper.append_unique(chain_list, item['chain'])
        helper.update_unique(balances_dict, item['chain'], {})
        helper.update_unique(balances_dict, item['notary'], {})
        helper.update_unique(balances_dict[item['notary']], item['chain'], 0)

        bal = balances_dict[item['notary']][item['chain']] + item['balance']
        balances_dict[item['notary']].update({item['chain']: bal})

    chain_list.sort()
    notary_list.sort()
    notary_list = helper.region_sort(notary_list)

    coins_dict = helper.get_dpow_server_coins_dict(season)
    main_chains = helper.get_mainnet_chains(coins_dict)
    third_chains = helper.get_third_party_chains(coins_dict)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain + " Notary Balances"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(COLORS["AR_REGION"])
            elif notary.endswith("_EU"):
                bg_color.append(COLORS["EU_REGION"])
            elif notary.endswith("_NA"):
                bg_color.append(COLORS["NA_REGION"])
            elif notary.endswith("_SH"):
                bg_color.append(COLORS["SH_REGION"])
            else:
                bg_color.append(COLORS["DEV_REGION"])
            border_color.append(COLORS["BLACK"])

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary + " Notary Balances"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            elif chain in main_chains:
                bg_color.append(COLORS["MAIN_COLOR"])
            else:
                bg_color.append(COLORS["OTHER_COIN_COLOR"])
            border_color.append(COLORS["BLACK"])

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
    labels = []
    bg_color = []
    chartdata = []
    chain_list = []
    main_chains = []
    notary_list = []
    border_color = []
    third_chains = []
    ntx_dict = {}
    filter_kwargs = {}

    notarised_date = helper.get_or_none(request, "notarised_date")
    season = helper.get_or_none(request, "season", SEASON)
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if not notarised_date or not season or (not chain and not notary):
        return {
            "error": "You need to specify both of the following \
                      filter parameters: ['notarised_date', 'season'] \
                      and at least one of the following \
                      ['notary', 'chain']"
        }

    coins_dict = helper.get_dpow_server_coins_dict(season)
    main_chains = helper.get_mainnet_chains(coins_dict)
    third_chains = helper.get_third_party_chains(coins_dict)

    data = query.get_notarised_count_daily_data(notarised_date, notary)
    data = data.values('notary', 'notarised_date', 'chain_ntx_counts')

    for item in data:
        helper.append_unique(notary_list, item['notary'])
        chain_list += list(item['chain_ntx_counts'].keys())
        ntx_dict.update({item['notary']: item['chain_ntx_counts']})

    chain_list = helper.get_or_none(request, "chain", list(set(chain_list)))
    
    chain_list.sort()
    notary_list.sort()
    notary_list = helper.region_sort(notary_list)

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain + " Notarisations"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(COLORS["AR_REGION"])
            elif notary.endswith("_EU"):
                bg_color.append(COLORS["EU_REGION"])
            elif notary.endswith("_NA"):
                bg_color.append(COLORS["NA_REGION"])
            elif notary.endswith("_SH"):
                bg_color.append(COLORS["SH_REGION"])
            else:
                bg_color.append(COLORS["DEV_REGION"])
            border_color.append(COLORS["BLACK"])

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary + " Notarisations"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            elif chain in main_chains:
                bg_color.append(COLORS["MAIN_COLOR"])
            else:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            border_color.append(COLORS["LT_BLUE"])

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

