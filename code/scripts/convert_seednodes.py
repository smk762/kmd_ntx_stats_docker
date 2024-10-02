
import csv
import json
from logger import logger

seednodes = {"Season_8": {}}
with open('s8_seednodes.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        logger.info(row)
        seednodes["Season_8"].update({
	        row[0]: {
	            "IP": row[2],
	            "PeerID": row[1]
        	}
        })

with open('notary_seednodes.json', 'w') as f:
	json.dump(seednodes, f, indent=4)	






