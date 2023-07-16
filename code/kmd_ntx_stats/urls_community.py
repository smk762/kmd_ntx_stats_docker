from django.urls import path
from kmd_ntx_api import community_views

# TOOL VIEWS
frontend_community_urls = [

    path('community/cryptopuzzles/',
          community_views.puzzles_view,
          name='puzzles_view'),

]


# API TOOLS V2
api_tool_urls = []