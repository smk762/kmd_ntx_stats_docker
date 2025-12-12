#!/usr/bin/env python3.12
import time
from django.http import HttpResponse

from kmd_ntx_api.logger import logger
from kmd_ntx_api.query import get_coin_last_ntx_data
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.cache_data import cached

# Status thresholds (seconds)
ACTIVE_MAX_AGE = 60 * 60 * 2.5  # 2.5 hours
IRREGULAR_MAX_AGE = 60 * 60 * 24  # 24 hours


def _badge_svg(label: str, message: str, color: str) -> str:
    """Return a simple two-part badge SVG (lightweight shields-like)."""
    # Basic sizing heuristics (monospace-ish)
    label_width = max(50, 6 * len(label) + 20)
    message_width = max(60, 7 * len(message) + 20)
    total_width = label_width + message_width
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {message}">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="round">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#round)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{message_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="start" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="10" y="14">{label}</text>
    <text x="{label_width + 10}" y="14">{message}</text>
  </g>
</svg>"""
    return svg


def status_from_timestamp(last_ts: int) -> str:
    """Map last notarisation timestamp to status."""
    if not last_ts or last_ts <= 0:
        return "inactive"
    age = time.time() - last_ts
    if age < ACTIVE_MAX_AGE:
        return "active"
    if age < IRREGULAR_MAX_AGE:
        return "irregular"
    return "inactive"


def color_for_status(status: str) -> str:
    return {
        "active": "#4c1",       # green
        "irregular": "#dfb317", # yellow
        "inactive": "#e05d44"   # red
    }.get(status, "#9f9f9f")


def coin_badge(request, coin: str):
    """Return a badge SVG for the given coin's last notarisation status."""
    season = get_page_season(request)
    cache_key = f"badge_svg_{season}_{coin}".lower()

    svg = cached.get_data(cache_key)
    if svg:
        return HttpResponse(svg, content_type="image/svg+xml")

    qs = get_coin_last_ntx_data(season=season, coin=coin)
    qs = qs.order_by("-kmd_ntx_blocktime")
    last_ts = 0
    try:
        last_ts = qs.values_list("kmd_ntx_blocktime", flat=True).first() or 0
    except Exception as e:
        logger.warning(f"[coin_badge] failed to fetch last_ts for {coin}: {e}")

    status = status_from_timestamp(last_ts)
    color = color_for_status(status)
    svg = _badge_svg(f"{coin.upper()} dPoW", status, color)

    # Cache short-term to avoid churn; keep within 5 minutes
    cached.refresh(key=cache_key, data=svg, expire=300, force=True)
    return HttpResponse(svg, content_type="image/svg+xml")

