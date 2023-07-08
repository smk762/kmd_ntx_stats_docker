source .env
sqlite3 $MM2_DB "SELECT * FROM stats_nodes limit 10;"
