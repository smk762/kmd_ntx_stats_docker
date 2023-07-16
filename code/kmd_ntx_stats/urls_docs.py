from django.urls import path
from kmd_ntx_api import doc_views

# DOC VIEWS
doc_urls = [
    path('docs/api_guide/',
          doc_views.doc_api_guide,
          name='doc_api_guide'),

    path('docs/yaml_api_guide/',
          doc_views.yaml_api_guide,
          name='yaml_api_guide'),

    path('docs/json_api_guide/',
          doc_views.json_api_guide,
          name='json_api_guide')
]

