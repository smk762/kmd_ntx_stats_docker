#!/usr/bin/env python3.12
import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when run via docker exec/cron
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
from django.conf import settings

# Setup Django
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmd_ntx_stats.settings")
    django.setup()

from kmd_ntx_api.mining import warm_mining_cache
from kmd_ntx_api.notary_seasons import get_season
from kmd_ntx_api.logger import logger


def main():
    season = get_season()
    count = warm_mining_cache(season)
    logger.info(f"[cron_warm_mining_cache] warmed {count} mining summaries for {season}")


if __name__ == "__main__":
    main()

