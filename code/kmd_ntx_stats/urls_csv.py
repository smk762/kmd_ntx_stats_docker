from django.urls import path

from kmd_ntx_api import api_csv


# CSV VIEWS
api_csv_urls = [
    path('api/csv/mined/',
         api_csv.mined_csv,
         name='mined_csv'),
]