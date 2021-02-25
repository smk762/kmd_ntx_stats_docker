#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
#table = 'notarised'
#table = 'mined'
#table = 'mined_count_season'
table = 'nn_btc_tx'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

#cursor.execute("DELETE FROM "+table+" WHERE output_index=1000 or input_index=1000;")
# [('Low Vin NTX',), ('Split',), ('NTX',), ('previous season funds transfer',), ('No Vout NTX',), ('Top Up',), ('Incoming Replenish',), ('MadMax personal top up',), ('Low Vin, No Vout NTX',), ('Consolidate',), ('SPAM',)]
#for i in ['Other', 'Low Vin NTX', 'No Vout NTX', 'Top Up', 'Incoming Replenish', 'Low Vin, No Vout NTX', 'Consolidate']:
#    cursor.execute(f"DELETE FROM {table} WHERE category='{i}';")
#    conn.commit()

cursor.execute("DELETE FROM coins;")
#cursor.execute("DELETE FROM "+table+" WHERE category='No Vout NTX' or category='Low Vin NTX' or category='Incoming Replenish';")

#cursor.execute("DELETE FROM "+table+" WHERE txid='b05e743a6ad8e419aef37d2c4a0f3882e4737115fe26812c7289df3372a4167f';")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("SELECT DISTINCT category FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

