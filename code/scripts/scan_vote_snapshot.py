#!/usr/bin/env python3
import json
from lib_helper import get_nn_region_split
from notary_candidates import CANDIDATE_ADDRESSES


with open('VOTE2022_22920.json', 'r') as j:
    votes = json.load(j)

candidate_votes = {}
for address in votes["addresses"]:
    if address["addr"] in CANDIDATE_ADDRESSES["VOTE2022"]:
        candidate_votes.update({
            CANDIDATE_ADDRESSES["VOTE2022"][address["addr"]]: address["amount"]
        })


with open('candidate_VOTE2022_22920.json', 'w') as j:
    json.dump(candidate_votes, j, indent=4)

regions = {}
region_scores = {}
for i in candidate_votes:
    candidate, region = get_nn_region_split(i)
    if region not in regions:
        region_scores.update({region:[]})
        regions.update({region:{}})

    region_scores[region].append(float(candidate_votes[i]))
    regions[region].update({
        candidate: {
            "sum_votes": float(candidate_votes[i])
        } 
    })


for region in regions:
    print(region)
    region_scores[region].sort()
    print(region_scores[region])    
    region_scores[region].reverse()
    print(region_scores[region])

for region in regions:
    for nn in regions[region]:
        rank = region_scores[region].index(regions[region][nn]["sum_votes"]) + 1
        regions[region][nn].update({"region_rank": rank})


with open('regional_VOTE2022_22920.json', 'w') as j:
    json.dump(regions, j, indent=4)
