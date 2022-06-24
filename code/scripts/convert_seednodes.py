
import csv
import json

seednodes = {"Season_6": {}}
with open('s6_seednodes.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
        seednodes["Season_6"].update({
	        row[0]: {
	            "IP": row[2],
	            "PeerID": row[1]
        	}
        })

with open('notary_seednodes.json', 'w') as f:
	json.dump(seednodes, f, indent=4)	






