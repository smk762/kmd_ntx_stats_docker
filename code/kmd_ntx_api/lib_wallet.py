
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper

def get_source_addresses(request):
    season = helper.get_or_none(request, "season")
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    return query.get_addresses_data(season, server, chain, notary)


def get_source_balances(request):
    season = helper.get_or_none(request, "season")
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    return query.get_balances_data(season, server, chain, notary)
