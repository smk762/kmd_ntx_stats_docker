from django import forms

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_mm2 import *
from kmd_ntx_api.widgets import *



class MakerbotForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MakerbotForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    mm2_coins = get_mm2_coins_list()
    TF_CHOICES = [(True,True), (False,False)]
    COIN_CHOICES = [(i,i) for i in mm2_coins]
    base = forms.ChoiceField(
        label='Coin to Sell',
        required=True,
        widget=forms.Select,
        choices=COIN_CHOICES
        )
    rel = forms.ChoiceField(
        label='Coin to Buy',
        required=True,
        widget=forms.Select,
        choices=COIN_CHOICES
        )
    price_elipsed_validity = forms.IntegerField(
        label='Maximum age of price data',
        initial=300,
        min_value=30,
        max_value=1800
        )
    max_trade = forms.FloatField(
        label='Percentage of balance to trade',
        required=False,
        initial=100,
        min_value=1,
        max_value=100
        )
    min_volume_usd = forms.FloatField(
        label='Minimum USD trade value accepted',
        initial=5,
        min_value=0.10
        )  # cant be used alongside min_volume
    spread = forms.FloatField(
        label='Percentage spread over market',
        initial=5,
        min_value=1,
        max_value=100
        )
    base_confs = forms.IntegerField(
        label='Sell side confirmations',
        initial=3,
        min_value=1,
        max_value=5
        )
    rel_confs = forms.IntegerField(
        label='Buy side confirmations',
        initial=3,
        min_value=1,
        max_value=5
        )

    base_nota = forms.ChoiceField(
        label='Sell side notarisations',
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )
    rel_nota = forms.ChoiceField(
        label='Buy side notarisations',
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )

    enable = forms.ChoiceField(
        label='Enable trading for pair?',
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )

    check_last_bidirectional_trade_thresh_hold = forms.ChoiceField(
        label="Only trade if price over VWAP",
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )
    
    price_url = forms.CharField(
        label="Price API",
        required=True,
        initial="http://price.cipig.net:1313/api/v2/tickers?expire_at=600"
        )
    
    bot_refresh_rate =  forms.IntegerField(
        label='Bot refresh rate',
        initial=60,
        min_value=30,
        max_value=1800
        )
    add_to_existing_config = forms.ChoiceField(
        label="Add to existing config",
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )
    create_bidirectional_config = forms.ChoiceField(
        label="Create bidirectional config",
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )

