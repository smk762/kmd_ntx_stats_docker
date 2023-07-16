#!/usr/bin/env python3
import requests
from django.shortcuts import render
from kmd_ntx_api.electrum import get_full_electrum_balance
from kmd_ntx_api.context import get_base_context

def puzzles_view(request):
    context = get_base_context(request)
    puzzles = {
        "August 2021": {
            "puzzle_images": [
                ('https://i.imgur.com/pkgUSxk.png', 'Scan for address'),
                ('https://i.imgur.com/WqSCQ8P.png', 'Watch on youtube'),
                ('https://i.imgur.com/wq2ETVN.png', 'Watch on youtube'),
                ('https://i.imgur.com/fwFN1ey.jpg', 'Not Caligula'),
                ('http://petslady.com/sites/default/files/inline-images/Screen_Shot_2015-09-06_at_10.08.12_AM.preview.png', 'Word placement hint'),
                ('https://upload.wikimedia.org/wikipedia/commons/e/e7/C-115_%28DHC-5_Buffalo%29_%2814367330899%29.jpg', 'Word placement hint'),
                ('https://www.masterofmalt.com/whiskies/american-eagle/american-eagle-12-year-old-whiskey.jpg', 'Word placement hint'),
            ],
            "puzzle_text": "Seed is 24 words and BIP39 compliant",
            "puzzle_value": get_full_electrum_balance(
                "electrum1.cipig.net",
                10001,
                "RUe4FBVXVGzN3KNYUF4EwwV4y3sZhQdJHh",
                None
            ),
            "puzzle_winner": None
        }
    }

    context.update({
        "page_title":"Cryptopuzzles!",
        "puzzles": puzzles
    })
    return render(request, 'views/community/cryptopuzzles.html', context)
