#!/usr/bin/env python3
import time
import requests
import logging
import logging.handlers
import lib_notary
import lib_const

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/elected_nn_social.json")
nn_social = r.json()

conn = lib_notary.connect_db()
cursor = conn.cursor()

season = "Season_4"
for notary in lib_const.NOTARY_PUBKEYS['Season_4']:
    notary_name = notary.split("_")[0]
    for region in nn_social[notary_name]['regions']:
        row_list = [notary_name+"_"+region]
        for social in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'keybase', 'website', 'icon']:
            if social in nn_social[notary_name]:
                if social == 'icon' and notary_name == 'swisscertifiers':
                    row_list.append('')
                else:
                    row_list.append(nn_social[notary_name][social])
            else:
                row_list.append("")
        row_list.append(season)
        row_data = tuple(row_list)

        lib_notary.update_nn_social_tbl(conn, cursor, row_data)
    

cursor.close()

conn.close()
