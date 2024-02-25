source .env
sqlite3 $MM2_DB "SELECT * FROM stats_nodes ORDER BY id DESC LIMIT 100"
