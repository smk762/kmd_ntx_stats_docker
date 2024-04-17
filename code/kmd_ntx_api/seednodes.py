
#### SEEDNODES 
import time
from datetime import datetime as dt
from datetime import timezone

from django.db.models import Sum
from kmd_ntx_api.helper import get_notary_list, get_or_none, get_notary_list, \
    date_hour, get_month_epoch_range, prepopulate_seednode_version_month, \
    prepopulate_seednode_version_date
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.cache_data import version_timespans_cache
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.query import get_seednode_version_stats_data

def seednode_version_context(request):
    active_version = " & ".join(get_active_mm2_versions(time.time()))
    day_version_scores = get_seednode_version_date_table(request)
    month_version_scores = get_seednode_version_month_table(request)

    return {
        "page_title": "AtomicDEX Seednode Stats",
        "active_version": active_version,
        "day_date": day_version_scores["date"],
        "day_start": int(day_version_scores["start"]),
        "day_end": int(day_version_scores["end"]),
        "day_date_ts": int(day_version_scores["start"]*1000),
        "day_table_data": day_version_scores["table_data"],
        "day_headers": day_version_scores["headers"],
        "day_scores": day_version_scores["scores"],
        "month_date": month_version_scores["date"],
        "month_date_ts": month_version_scores["date_ts"],
        "month_table_data": month_version_scores["table_data"],
        "month_headers": month_version_scores["headers"],
        "month_scores": month_version_scores["scores"]
    }


def get_active_mm2_versions(ts):
    active_versions = []
    versions = version_timespans_cache()
    for version in versions:
        if int(ts) < versions[version]["end"]:
            active_versions.append(version)
    return active_versions


def is_mm2_version_valid(version, timestamp):
    active_versions = get_active_mm2_versions(timestamp)
    if version in active_versions:
        return True
    return False


def get_seednode_version_date_table(request):
    season = get_page_season(request)
    start = int(get_or_none(request, "start", time.time() - SINCE_INTERVALS["day"]))
    end = int(get_or_none(request, "end", time.time()))
    notary_list = get_notary_list(season)
    default_scores = prepopulate_seednode_version_date(notary_list)
    hour_headers = list(default_scores.keys())
    hour_headers.sort()
    table_headers = ["Notary"] + hour_headers + ["Total"]
    data = get_seednode_version_stats_data(start=start, end=end)
    scores = data.values()
    for item in scores:
        notary = item["name"]
        if notary in notary_list:
            score = item["score"]
            _, hour = date_hour(item["timestamp"]).split(" ")
            hour = hour.replace(":00", "")

            default_scores[hour][notary]["score"] = score
            if item["version"] not in default_scores[hour][notary]["versions"]:
                default_scores[hour][notary]["versions"].append(item["version"])

    table_data = []
    for notary in notary_list:
        notary_row = {"Notary": notary}
        total = 0
        for hour in hour_headers:
            if default_scores[hour][notary]["score"] == 0.2:
                total += default_scores[hour][notary]["score"]
            elif default_scores[hour][notary]["score"] == 0.01:
                default_scores[hour][notary]["score"] = f'0 (WSS connection failing)'
            elif default_scores[hour][notary]["score"] == 0:
                default_scores[hour][notary]["score"] = f'0 (Wrong version: {default_scores[hour][notary]["versions"]})'
            notary_row.update({
                hour: default_scores[hour][notary]["score"]
            })
        notary_row.update({
            "Total": round(total,1)
        })
        table_data.append(notary_row)
    return {
        "start": start,
        "date": dt.utcfromtimestamp(end).strftime('%a %-d %B %Y'),
        "end": end,
        "headers": table_headers,
        "table_data": table_data,
        "scores": default_scores
    }


def get_seednode_version_month_table(request):
    season = get_page_season(request)
    year = get_or_none(request, "year", dt.now(timezone.utc).timestamp().year)
    month = get_or_none(request, "month", dt.now(timezone.utc).timestamp().month)
    start, end, last_day = get_month_epoch_range(year, month)
    notary_list = get_notary_list(season)
    default_scores = prepopulate_seednode_version_month(notary_list)
    day_headers = list(default_scores.keys())
    day_headers.sort()
    table_headers = ["Notary"] + day_headers + ["Total"]
    data = get_seednode_version_stats_data(start=start, end=end).values()
    for item in data:
        notary = item["name"]
        if notary in notary_list:
            score = item["score"]
            if score == 0.2:
                date, _ = date_hour(item["timestamp"]).split(" ")
                day = date.split("/")[1]
                default_scores[day][notary]["score"] += score
                if item["version"] not in default_scores[day][notary]["versions"]:
                    default_scores[day][notary]["versions"].append(item["version"])
    table_data = []
    for notary in notary_list:
        notary_row = {"Notary": notary}
        total = 0
        for day in day_headers:
            total += default_scores[day][notary]["score"]
            notary_row.update({
                day: default_scores[day][notary]["score"]
            })
        notary_row.update({
            "Total": round(total,1)
        })
        table_data.append(notary_row)
    return {
        "date_ts": dt.utcfromtimestamp(end).strftime('%m-%Y'),
        "date": dt.utcfromtimestamp(end).strftime('%b %Y'),
        "headers": table_headers,
        "table_data": table_data,
        "scores": default_scores
    }

def get_seednode_version_score_total(request, season=None, start=None, end=None):
    if not season:
        season = get_page_season(request)
    notary_list = get_notary_list(season)
    start = get_or_none(request, "start", start)
    if not start: start = int(time.time()) - SINCE_INTERVALS["day"]
    end = get_or_none(request, "end", end)
    if not end: end = int(time.time())
    data = get_seednode_version_stats_data(start=start, end=end)
    notary_scores = list(data.values('name').order_by('name').annotate(sum_score=Sum('score')))
    notaries_with_scores = data.distinct('name').values_list('name', flat=True)
    for notary in notary_list:
        if notary not in notaries_with_scores:
            notary_scores.append({"name": notary, "sum_score": 0})
    resp = {}
    for i in notary_scores:
        if i["name"] in notary_list:
            resp.update({i["name"]: round(i["sum_score"],2)})
    return resp
