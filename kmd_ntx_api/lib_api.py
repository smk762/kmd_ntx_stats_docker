#!/usr/bin/env python3


def paginate_wrap(resp, url, field, prev_value, next_value):
    api_resp = {
        "count":len(resp),
        "next":url+"?"+field+"="+next_value,
        "previous":url+"?"+field+"="+prev_value,
        "results":[resp]
    }
    return api_resp


def wrap_api(resp, filters=None):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    if filters:
        api_resp.update({"filters":filters})
    return api_resp
