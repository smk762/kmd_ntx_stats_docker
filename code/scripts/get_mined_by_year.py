import lib_query

rewards = {}
for year in range(2016, 2024):
    r = lib_query.get_rewards_year_aggregates(year)
    if r[0][0] > 0:
        resp = {
            "claims": r[0][0],
            "value": float(r[0][1])
        }
        rewards.update({str(year): resp})

r = lib_query.get_rewards_since_genesis()
resp = {
    "claims": r[0][0],
    "value": float(r[0][1])
}
rewards.update({"since_genesis": resp})

for i in rewards:
    print(f"Rewards {i}: {rewards[i]['claims']} claims, {rewards[i]['value']} KMD value")


mined = {}
for year in range(2016, 2024):
    r = lib_query.get_mined_year_aggregates(year)
    if r[0][0] > 0:
        resp = {
            "blocks": r[0][0],
            "value": float(r[0][1])
        }
        mined.update({str(year) : resp})

r = lib_query.get_mined_since_genesis()
resp = {
    "blocks": r[0][0],
    "value": float(r[0][1])
}
mined.update({"since_genesis": resp})

for i in mined:
    print(f"Mined {i}: {mined[i]['blocks']} blocks, {mined[i]['value']} KMD value")