#!/usr/bin/env python3.12

import json
import requests

all_data = []
next_url = "http://116.203.120.91:8762/api/source/mined/"

while next_url:
	print(next_url)
	data = requests.get(next_url).json()
	next_url = data["next"]

	for block in data["results"]:
		block.update({"unclaimed_portion": float(block["value"]) - 3})
		all_data.append(block)

with open('mining_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)