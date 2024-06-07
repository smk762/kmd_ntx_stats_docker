
import csv
import json
from logger import logger

seednodes = {"Season_7": {}}
with open('s7_seednodes.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        logger.info(row)
        seednodes["Season_7"].update({
	        row[0]: {
	            "IP": row[2],
	            "PeerID": row[1]
        	}
        })

with open('notary_seednodes.json', 'w') as f:
	json.dump(seednodes, f, indent=4)	






