#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
#table = 'nn_social'
#table = 'mined'
#table = 'mined_count_season'
table = 'notarised_tenure'
#table = 'notarised'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

# cursor.execute("DELETE FROM "+table+" WHERE output_index=1000 or input_index=1000;")
# [('Low Vin NTX',), ('Split',), ('NTX',), ('previous season funds transfer',), ('No Vout NTX',), ('Top Up',), ('Incoming Replenish',), ('MadMax personal top up',), ('Low Vin, No Vout NTX',), ('Consolidate',), ('SPAM',)]
# for i in ['Other', 'Low Vin NTX', 'No Vout NTX', 'Top Up', 'Incoming Replenish', 'Low Vin, No Vout NTX', 'Consolidate']:
#    cursor.execute(f"DELETE FROM {table} WHERE category='{i}';")
#    conn.commit()

#cursor.execute("DELETE FROM "+table+" WHERE chain = 'LTC';")
#cursor.execute("DELETE FROM "+table+" WHERE season = 'Season_4';")
cursor.execute("DELETE FROM "+table+";")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("SELECT DISTINCT category FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

