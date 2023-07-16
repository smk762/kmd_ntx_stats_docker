import random
from kmd_ntx_api.helper import get_or_none, get_notary_list, get_page_server, \
    get_notary_clean, get_dpow_coins, get_notary_list, get_eco_data_link, \
    get_sidebar_links, get_random_notary
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.cache_data import explorers_cache, coin_icons_cache, notary_icons_cache, navigation_cache


def get_base_context(request):
    season = get_page_season(request)
    notary = get_or_none(request, "notary", get_random_notary(season))
    epoch = get_or_none(request, "epoch", "Epoch_0")
    selected = {}
    [selected.update({i: request.GET[i]}) for i in request.GET]
    context = {
        "season": season,
        "season_clean": season.replace("_"," "),
        "server": get_page_server(request),
        "epoch": epoch,
        "coin": get_or_none(request, "coin", "KMD"),
        "notary": notary,
        "notary_clean": get_notary_clean(notary),
        "year": get_or_none(request, "year"),
        "month": get_or_none(request, "month"),
        "address": get_or_none(request, "address"),
        "selected": selected,
        "hide_filters": get_or_none(request, "hide_filters", []),
        "region": get_or_none(request, "region", "EU"),
        "regions": ["AR", "EU", "NA", "SH", "DEV"],
        "epoch_clean": epoch.replace("_"," "),
        "explorers": explorers_cache(), 
        "coin_icons": coin_icons_cache(),
        "dpow_coins": get_dpow_coins(season, True),
        "notary_icons": notary_icons_cache(season),
        "notaries": get_notary_list(season),
        "sidebar_links": get_sidebar_links(season),
        "nav_data": navigation_cache(),
        "eco_data_link": get_eco_data_link()
    }
    return context