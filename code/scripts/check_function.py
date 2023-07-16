#!/usr/bin/env python3
import json
import ntx

data = ntx.get_season_ntx_dict("Season_5")
print(json.dumps(data, indent=4))