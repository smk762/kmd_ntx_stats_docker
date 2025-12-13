import os
from django.apps import AppConfig

from kmd_ntx_api.cache_data import cached
from kmd_ntx_api.logger import logger
from kmd_ntx_api.notary_seasons import get_seasons_info

try:
    # Full season/epoch context and dPoW active computation lives in scripts.
    from scripts.const_seasons import SEASONS as CONST_SEASONS
except Exception:  # pragma: no cover - optional in some runtimes
    CONST_SEASONS = None


class KmdNtxApiConfig(AppConfig):
    name = 'kmd_ntx_api'

    def ready(self):
        """Warm critical caches on Django startup."""
        if os.getenv("SKIP_CACHE_WARMUP") == "True":
            logger.info("Cache warmup skipped via SKIP_CACHE_WARMUP")
            return

        # Force scoring epochs fetch/cache before anything else so servers/epochs populate
        if CONST_SEASONS:
            try:
                CONST_SEASONS.__dict__.pop("epochs_repo_data", None)
                CONST_SEASONS.__dict__.pop("epochs", None)
                epoch_data = CONST_SEASONS.epochs_repo_data  # trigger fetch/cache with logging
                epoch_count = len(epoch_data or {})
                logger.info(f"epochs_repo_data primed with {epoch_count} seasons")
                if epoch_count == 0:
                    logger.warning("epochs_repo_data empty after fetch; check scoring_epochs fetch/cached file")
            except Exception as e:
                logger.warning(f"Failed to prime epochs_repo_data: {e}")

        # 1) Build/populate notary_seasons with coins/epochs/servers.
        try:
            get_seasons_info()  # get_seasons_info writes via cached.refresh
            logger.info("notary_seasons cache warmed on startup")
        except Exception as e:  # pragma: no cover - startup guard
            logger.warning(f"Failed to warm notary_seasons: {e}")

        # 2) Build dpow_active_coins using const_seasons epoch logic.
        if CONST_SEASONS:
            try:
                season, active_details, _ = CONST_SEASONS.get_dpow_active_info()
                # Do not overwrite with empty data; rely on cached scoring_epochs fallback in const_seasons
                if active_details:
                    cached.bump_epoch("epochs")
                    cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
                    cached.refresh(key=cache_key, data=active_details, force=True, expire=900)
                    logger.info("dpow_active_coins cache warmed on startup")
                else:
                    logger.warning("dpow_active_coins not warmed: active_details empty")
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to warm dpow_active_coins: {e}")
        else:
            try:
                cached.bump_epoch("epochs")
                cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
                cached.refresh(key=cache_key, data={}, force=True, expire=900)
            except Exception:
                pass
