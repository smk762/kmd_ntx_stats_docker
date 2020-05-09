#!/usr/bin/env python3

import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()
for table in ['notarised']:
	table_lib.ts_col_to_season_col(conn, cursor, 'block_time', "season", table)
cursor.close()

conn.close()