from datetime import datetime as dt
from django.db.models import Sum, Count
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.query import get_notary_vote_data, get_notary_candidates_data
from kmd_ntx_api.serializers import notaryVoteSerializer

VOTE_YEAR = "VOTE2022"

VOTE_PERIODS = {
    "VOTE2021": {
        "max_block": 20492
    },
    "VOTE2022": {
        "max_block": 20492,
        "max_blocktime": 1653523199
    }
}

def get_vote_aggregates(request):
    candidate = get_or_none(request, "candidate")
    year = get_or_none(request, "year", VOTE_YEAR)

    data = list(get_notary_vote_data(year).values('candidate', 'votes'))
    resp = {}
    for item in data:
        candidate = item["candidate"]
        if candidate not in resp:
            resp.update({candidate:{"votes": 0}})
        resp[candidate]["votes"] += item["votes"]

    return resp


def is_election_over(year):
    final_block = 22920
    return f"Election complete! Final VOTE2022 block height: <a href='https://vote2022.komodod.com/b/{final_block}'>{final_block}</a>" 

def get_vote_stats_info(request):
    resp = get_notary_vote_stats_info(request)

    proposals = get_candidates_proposals(request)

    for region in resp:
        for item in resp[region]:
            notary = translate_candidate_to_proposal_name(item["candidate"])
            item.update({
                "proposal": proposals[notary.lower()]
            })
    return resp


def get_notary_vote_detail_table(request):
    year = get_or_none(request, "year", VOTE_YEAR)
    candidate = get_or_none(request, "candidate")
    proposals = get_candidates_proposals(request)
    notary_vote_detail_table = get_notary_vote_table(request)

    for item in notary_vote_detail_table:
        notary = translate_candidate_to_proposal_name(item["candidate"])
        item.update({
            "proposal": proposals[notary.lower()]
        })

    if candidate:
        candidate = request.GET["candidate"].replace(".", "-")

    if 'results' in notary_vote_detail_table:
        notary_vote_detail_table = notary_vote_detail_table["results"]

    for item in notary_vote_detail_table:
        date_time = dt.utcfromtimestamp(item["block_time"])

        item.update({"block_time_human":date_time.strftime("%m/%d/%Y, %H:%M:%S")})
    return notary_vote_detail_table

def get_notary_vote_stats_info(request):
    year = get_or_none(request, "year")
    candidate = get_or_none(request, "candidate")
    block = get_or_none(request, "block")
    txid = get_or_none(request, "txid")
    min_block = get_or_none(request, "min_block")
    min_blocktime = get_or_none(request, "min_blocktime")
    min_locktime = get_or_none(request, "min_locktime")
    max_block = get_or_none(request, "max_block")
    max_blocktime = get_or_none(request, "max_blocktime")
    max_locktime = get_or_none(request, "max_locktime")
    year = get_or_none(request, "year", VOTE_YEAR)

    data = get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, None, True)
    data = data.values('candidate', 'candidate_address').annotate(num_votes=Count('votes'), sum_votes=Sum('votes'))
    unverified = get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, None, False)
    unverified = unverified.values('candidate').annotate(sum_votes=Sum('votes'))

    unverified_resp = {}
    for item in unverified:
        region = item["candidate"].split("_")[-1]
        if region not in unverified_resp:
            unverified_resp.update({region:{}})
        unverified_resp[region].update({
            item["candidate"]: item["sum_votes"]
        })

    resp = {
        "AR": [],
        "EU": [],
        "NA": [],
        "SH": []
    }
    region_scores = {
        "AR": [],
        "EU": [],
        "NA": [],
        "SH": []
    }
    for item in data:
        region = item["candidate"].split("_")[-1]

        ghost_votes = 0
        if region in unverified_resp:
            if item["candidate"] in unverified_resp[region]:
                ghost_votes = unverified_resp[region][item["candidate"]]
            

        item.update({
            "unverified": ghost_votes
        })
        resp[region].append(item)
        region_scores[region].append(item["sum_votes"])

    for region in resp:
        region_scores[region].sort()
        region_scores[region].reverse()
        for item in resp[region]:
            rank = region_scores[region].index(item["sum_votes"]) + 1
            item.update({"region_rank": rank})

    for region in resp:
        resp[region] = sorted(resp[region], key = lambda item: item['region_rank'])

    return resp


def get_notary_vote_table(request):
    candidate = get_or_none(request, "candidate")
    block = get_or_none(request, "block")
    txid = get_or_none(request, "txid")
    mined_by = get_or_none(request, "mined_by")
    max_block = get_or_none(request, "max_block")
    max_blocktime = get_or_none(request, "max_blocktime")
    max_locktime = get_or_none(request, "max_locktime")
    year = get_or_none(request, "year", VOTE_YEAR)


    data = get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, mined_by)

    if "order_by" in request.GET:
        order_by = request.GET["order_by"]
        data = data.order_by(f'-{order_by}').values()
    else:
        data = data.order_by(f'-block_time').values()

    serializer = notaryVoteSerializer(data, many=True)
    resp = {}
    for item in serializer.data:
        item.update({"lag": item["block_time"]-item["lock_time"]})

    return serializer.data



def translate_proposal_name_to_candidate(name, candidates):
    if name == "metaphilbert":
        name =  "metaphilibert"
    if name == "xenbug":
        name = "xen"
    if name == "who-biz":
        return "biz"
    for candidate in candidates:
        if candidate.lower().find(name.lower()) > -1:
            return candidate.lower()
    return name
    


def get_candidates_proposals(request):
    data = get_notary_candidates_data(VOTE_YEAR).values()
    props = {}
    for item in data:
        notary = item['name'].lower()
        if notary not in props:
            props.update({notary:item["proposal_url"]})
    return props


def translate_candidate_to_proposal_name(notary):
    x = notary.split("_")
    region = x[-1]
    notary = notary.replace(f"_{region}", "")
    if notary == "shadowbit":
        return "decker"
    if notary == "kolo2":
        return "kolo"
    if notary == "phit":
        return "phm87"
    if notary == "cipi2":
        return "cipi"
    if notary == "vanbogan":
        return "van"
    if notary == "metaphilbert":
        return "metaphilibert"
    if notary == "xenbug":
        return "xen"
    if notary == "marmara":
        return "marmarachain"
    if notary == "biz":
        return "who-biz"
    return notary
