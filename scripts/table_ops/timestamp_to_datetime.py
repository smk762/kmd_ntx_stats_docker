#!/usr/bin/env python3

import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()
for table in ['mined', 'notarised']:
	table_lib.ts_col_to_dt_col(conn, cursor, 'block_time', "block_datetime", table)
cursor.close()

conn.close()