from .lib_helper import get_or_none
from .lib_query import get_addresses_data, get_balances_data


def get_source_addresses(request):
    season = get_or_none(request, "season")
    server = get_or_none(request, "server")
    chain = get_or_none(request, "chain")
    notary = get_or_none(request, "notary")
    return get_addresses_data(season, server, chain, notary)


def get_source_balances(request):
    season = get_or_none(request, "season")
    server = get_or_none(request, "server")
    chain = get_or_none(request, "chain")
    notary = get_or_none(request, "notary")
    return get_balances_data(season, server, chain, notary)
