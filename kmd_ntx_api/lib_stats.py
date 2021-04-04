
def get_region_score_stats(notarisation_scores):
    region_score_stats = {}
    for region in notarisation_scores:
        region_total = 0
        notary_count = 0
        for notary in notarisation_scores[region]:
            notary_count += 1
            region_total += notarisation_scores[region][notary]["score"]
        region_average = region_total/notary_count
        region_score_stats.update({
            region:{
                "notary_count": notary_count,
                "total_score": region_total,
                "average_score": region_average
            }
        })
    return region_score_stats


def get_top_region_notarisers(region_notary_ranks):
    top_region_notarisers = {
        "AR":{
        },
        "EU":{
        },
        "NA":{
        },
        "SH":{
        },
        "DEV":{
        }
    }
    top_ntx_count = {}
    for region in region_notary_ranks:
        if region not in top_ntx_count:
            top_ntx_count.update({region:{}})
        for notary in region_notary_ranks[region]:
            for chain in region_notary_ranks[region][notary]:
                if chain not in top_ntx_count:
                    top_ntx_count[region].update({chain:0})

                if chain not in top_region_notarisers[region]:
                    top_region_notarisers[region].update({chain:{}})

                ntx_count = region_notary_ranks[region][notary][chain]
                if ntx_count > top_ntx_count[region][chain]:
                    top_notary = notary
                    top_ntx_count[region].update({chain:ntx_count})
                    top_region_notarisers[region][chain].update({
                        "top_notary": top_notary,
                        "top_ntx_count": top_ntx_count[region][chain]

                    })
    return top_region_notarisers

def get_top_coin_notarisers(top_region_notarisers, chain):
    top_coin_notarisers = {}
    for region in top_region_notarisers:
        if chain in top_region_notarisers[region]:
            top_coin_notarisers.update({
                region:{
                    "top_notary": top_region_notarisers[region][chain]["top_notary"],
                    "top_ntx_count": top_region_notarisers[region][chain]["top_ntx_count"]
                }
            })
    return top_coin_notarisers