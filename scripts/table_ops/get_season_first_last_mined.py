#!/usr/bin/env python3
import logging
import logging.handlers
from notary_info import season_addresses
from dotenv import load_dotenv
import psycopg2

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
load_dotenv()

conn = psycopg2.connect(
  host='localhost',
  user='postgres',
  password='postgres',
  port = "7654",
  database='postgres'
)
cursor = conn.cursor()

season_info = {}
all_addresses = []
reused_addresses = []

s1_addresses = season_addresses['Season_1']
s2_addresses = season_addresses['Season_2']
s3_addresses = list(set(season_addresses['Season_3']+season_addresses['Season_3.5']+season_addresses['Season_3_Third_Party']))

unique_s1_addresses = [i for i in s1_addresses if i not in s2_addresses and i not in s3_addresses]
logger.info("unique_s1_addresses: "+str(len(unique_s1_addresses)))
logger.info('.')
unique_s2_addresses = [i for i in s2_addresses if i not in s1_addresses and i not in s3_addresses]
logger.info("unique_s2_addresses: "+str(len(unique_s2_addresses))) 
logger.info('.')
unique_s3_addresses = [i for i in s3_addresses if i not in s1_addresses and i not in s2_addresses]
logger.info("unique_s3_addresses: "+str(len(unique_s3_addresses)))
logger.info('.')

sql = "SELECT COUNT(*) FROM mined;"
cursor.execute(sql)
logger.info(str(cursor.fetchone())+" blocks mined)")
logger.info('.')

def get_season_info(season, season_unique_addr, season_info=None):
  if not season_info:
    season_info = {}
  sql = "SELECT MIN(block), MAX(block), \
         MIN(block_time), MAX(block_time) \
         FROM mined WHERE address IN "+str(tuple(season_unique_addr))+";" 
  # logger.info(sql)
  cursor.execute(sql)
  season_mined = cursor.fetchone()
  # logger.info(season_mined)
  if season_mined[0] is not None:
    season_info.update({
        season:{
          "min_block":season_mined[0],
          "max_block":season_mined[1],
          "min_block_time":season_mined[2],
          "max_block_time":season_mined[3]
        }
      })
    sql = "SELECT address, name FROM mined WHERE block = "+str(season_mined[0])+";"
    cursor.execute(sql)
    min_mined_by = cursor.fetchone()
    season_info[season].update({"min_mined_by_address": min_mined_by[0]})
    season_info[season].update({"min_mined_by_name": min_mined_by[1]})

    sql = "SELECT address, name FROM mined WHERE block = "+str(season_mined[1])+";"
    cursor.execute(sql)
    max_mined_by = cursor.fetchone()
    season_info[season].update({"max_mined_by_address": max_mined_by[0]})
    season_info[season].update({"max_mined_by_name": max_mined_by[1]})
    logger.info(season+": "+str(season_info[season]))
    logger.info('.')
  return season_info

season_info = get_season_info("Season_1", unique_s1_addresses)
season_info = get_season_info("Season_2", unique_s2_addresses, season_info)
season_info = get_season_info("Season_3", unique_s3_addresses, season_info)
# logger.info(season_info)

cursor.close()  