from django.urls import path

from kmd_ntx_api import csv_api


# CSV VIEWS
api_csv_urls = [
    path('api/csv/mined/',
         csv_api.mined_csv,
         name='mined_csv'),
]