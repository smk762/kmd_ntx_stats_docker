from .lib_query import get_addresses_data, get_balances_data

def get_source_addresses(request):
    season = None
    server = None
    chain = None
    notary = None

    if 'season' in request.GET:
        season = request.GET["season"]
    if 'server' in request.GET:
        server = request.GET["server"]
    if 'chain' in request.GET:
        chain = request.GET["chain"]
    if 'notary' in request.GET:
        notary = request.GET["notary"]

    return get_addresses_data(season, server, chain, notary)

def get_source_balances(request):
    season = None
    server = None
    chain = None
    notary = None

    if 'season' in request.GET:
        season = request.GET["season"]
    if 'server' in request.GET:
        server = request.GET["server"]
    if 'chain' in request.GET:
        chain = request.GET["chain"]
    if 'notary' in request.GET:
        notary = request.GET["notary"]

    return get_balances_data(season, server, chain, notary)
