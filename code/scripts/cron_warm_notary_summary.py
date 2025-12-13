#!/usr/bin/env python3.12
import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when run via docker exec/cron
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
from django.test import RequestFactory

# Setup Django
if not django.conf.settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmd_ntx_stats.settings")
    django.setup()

from kmd_ntx_api.logger import logger
from kmd_ntx_api.table import get_notary_ntx_season_table_data
from kmd_ntx_api.notary_seasons import get_seasons_info, get_page_season
from kmd_ntx_api.helper import get_notary_list


def main():
    seasons_info = get_seasons_info()
    season = get_page_season(RequestFactory().get("/"), seasons_info)
    notaries = get_notary_list(season, seasons_info)
    rf = RequestFactory()

    warmed = 0
    for notary in notaries:
        req = rf.get("/", {"season": season, "notary": notary})
        try:
            get_notary_ntx_season_table_data(req, notary)
            warmed += 1
        except Exception as e:
            logger.warning(f"[warm_notary_summary] failed for {notary}: {e}")

    logger.info(f"[warm_notary_summary] warmed {warmed} notary summaries for {season}")


if __name__ == "__main__":
    main()

