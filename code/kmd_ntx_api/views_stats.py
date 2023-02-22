#!/usr/bin/env python3
import math
import requests
from django.shortcuts import render

from datetime import datetime as dt

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.forms as forms



def bokeh_example_view(request):
    context = helper.get_base_context(request)
    context.update(graph.get_bokeh_example(request))
    context.update({
        "page_title": "Active User Rewards",
        "endpoint": "/api/table/tba/"
    })

    return render(request, 'views/stats/bokeh_example.html', context)


def rewards_scatterplot_view(request):
    context = helper.get_base_context(request)
    context.update(graph.get_rewards_scatterplot(request))
    context.update({
        "page_title": "Mining",
        "endpoint": "/api/table/tba/"
    })

    return render(request, 'views/stats/bokeh_example.html', context)



def block_production_view(request):
    context = helper.get_base_context(request)
    context.update(graph.get_block_production(request))
    context.update({
        "endpoint": "/api/table/tba/"
    })

    return render(request, 'views/stats/bokeh_example.html', context)

