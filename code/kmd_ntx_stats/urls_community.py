from django.urls import path
from kmd_ntx_api import community_views_unlisted

# TOOL VIEWS
frontend_community_urls = [

    path('community/cryptopuzzles/',
          community_views_unlisted.puzzles_view,
          name='puzzles_view'),

]


# API TOOLS V2
api_tool_urls = []