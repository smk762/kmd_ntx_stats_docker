from django.urls import path
from kmd_ntx_api import views_doc

# DOC VIEWS
doc_urls = [
    path('docs/api_guide/',
          views_doc.doc_api_guide,
          name='doc_api_guide'),

    path('docs/yaml_api_guide/',
          views_doc.yaml_api_guide,
          name='yaml_api_guide'),

    path('docs/json_api_guide/',
          views_doc.json_api_guide,
          name='json_api_guide')
]

