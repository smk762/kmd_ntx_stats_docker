#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table = 'notarised'
date_col = 'block_datetime'

date_list = table_lib.get_dates_list(cursor, table, date_col)
print(date_list[-1])
print(date_list[-2])
print(date_list[-3])
print(date_list[-4])
date_resp = table_lib.get_records_for_date(cursor, table, date_col, date_list[-1])
today_resp = table_lib.get_ntx_chain_coin_for_date(cursor, table, date_col, date_list[-1])
print(date_resp)
print(today_resp)

cursor.close()

conn.close()

