from django.urls import path
from kmd_ntx_api import views_community

# TOOL VIEWS
frontend_community_urls = [

    path('community/cryptopuzzles/',
          views_community.puzzles_view,
          name='puzzles_view'),

]


# API TOOLS V2
api_tool_urls = []