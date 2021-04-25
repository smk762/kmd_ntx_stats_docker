#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
#table = 'nn_social'
#table = 'mined'
#table = 'mined_count_season'
#table = 'notarised_tenure'
#table = 'notarised'
#table = 'coins'
#table = "scoring_epochs"
#table = 'nn_ltc_tx'
#table = 'addresses'
table = 'last_notarised'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

# cursor.execute("DELETE FROM "+table+" WHERE output_index=1000 or input_index=1000;")
# [('Low Vin NTX',), ('Split',), ('NTX',), ('previous season funds transfer',), ('No Vout NTX',), ('Top Up',), ('Incoming Replenish',), ('MadMax personal top up',), ('Low Vin, No Vout NTX',), ('Consolidate',), ('SPAM',)]
# for i in ['Other', 'Low Vin NTX', 'No Vout NTX', 'Top Up', 'Incoming Replenish', 'Low Vin, No Vout NTX', 'Consolidate']:
#    cursor.execute(f"DELETE FROM {table} WHERE category='{i}';")
#    conn.commit()

#cursor.execute("DELETE FROM "+table+" WHERE chain='LTC' AND season = 'Season_4';")
#cursor.execute("DELETE FROM "+table+" WHERE season = 'Season_4';")
#cursor.execute("DELETE FROM nn_ltc_tx WHERE category = 'Other';")
cursor.execute("DELETE FROM "+table+";")
#cursor.execute("DELETE FROM "+table+" WHERE season = 'Season_5_Testnet';")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

#cursor.execute("SELECT DISTINCT category FROM nn_btc_tx;")
#print(cursor.fetchall())

cursor.close()

conn.close()

