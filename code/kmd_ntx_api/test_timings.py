#!/usr/bin/env python3
import time

start = int(time.time())
get_mined_data(None, notary).values()
end = int(time.time())
print(f"get_mined_data: {end-start}")

start = end
get_notary_list("Season_5").values()
end = int(time.time())
print(f"get_notary_list: {end-start}")

start = end
get_sidebar_links("Season_5").values()
end = int(time.time())
print(f"get_sidebar_links: {end-start}")

start = end
get_eco_data_link("Season_5").values()
end = int(time.time())
print(f"get_eco_data_link: {end-start}")

