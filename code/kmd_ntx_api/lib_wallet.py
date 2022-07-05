from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers



def get_source_addresses(request):
    season = helper.get_or_none(request, "season")
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    return query.get_addresses_data(season, server, coin, notary)


def get_addresses_rows(request):
    filters = ["season", "server", "notary", "coin"]
    data = query.get_addresses_data()
    distinct = query.get_distinct_filters(data, filters)
    print(distinct)
    data = helper.apply_filters_api(
        request, serializers.addressesSerializer, data
    ).values()
    serializer = serializers.addressesSerializer(data, many=True)
    count = data.count()
    return {
        "filters": filters,
        "count": count,
        "distinct": distinct,
        "results": serializer.data,
    }


def get_source_balances(request):
    season = helper.get_or_none(request, "season")
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    return query.get_balances_data(season, server, coin, notary)


def get_balances_rows(request, notary=None, coin=None):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin", coin)
    notary = helper.get_or_none(request, "notary", notary)
    address = helper.get_or_none(request, "address")

    if not season and not coin and not notary and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin', 'notary', 'address']"
        }
    data = query.get_balances_data(season, server, coin, notary, address).order_by('notary', 'coin')
    data = data.values()

    serializer = serializers.balancesSerializer(data, many=True)

    return serializer.data