from django import forms

from kmd_ntx_api.info import get_mm2_coins_list

TF_CHOICES = [(True,True), (False,False)]
COIN_CHOICES = [(i,i) for i in get_mm2_coins_list()]

class MakerbotForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MakerbotForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields["max_trade_type"].widget.attrs['class'] = 'form-control clear_bhp input-lbl-dark text-left'
        self.fields["min_trade_type"].widget.attrs['class'] = 'form-control clear_bhp input-lbl-dark text-left'


    MAX_CHOICES = [
        ("percentage","Max. balance percentage to trade"),
        ("usd","Max. USD value to trade")
    ]
    MIN_CHOICES = [
        ("percentage","Min. balance percentage to trade"),
        ("usd","Min. USD value to trade")
    ]

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
        required=True,
        initial=300,
        min_value=30,
        max_value=1800
        )
    max_trade_type = forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=MAX_CHOICES
        )
    max_trade = forms.FloatField(
        label='Percentage of balance to trade',
        required=True,
        initial=100,
        min_value=1,
        max_value=100
        )
    min_trade_type = forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=MIN_CHOICES
        )
    min_trade = forms.FloatField(
        label='Percentage of balance to trade',
        required=True,
        initial=100,
        min_value=1,
        max_value=100
        )
    spread = forms.FloatField(
        label='Percentage spread over market',
        required=True,
        initial=5,
        min_value=1,
        max_value=100
        )
    base_confs = forms.IntegerField(
        label='Sell side confirmations',
        required=True,
        initial=3,
        min_value=1,
        max_value=5
        )
    rel_confs = forms.IntegerField(
        label='Buy side confirmations',
        required=True,
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
        initial="https://prices.cipig.net:1717/api/v2/tickers?expire_at=600"
        )
    
    bot_refresh_rate =  forms.IntegerField(
        label='Bot refresh rate',
        required=True,
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


class EnableCommandForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EnableCommandForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    coin = forms.ChoiceField(
        label='Coin to Enable',
        required=True,
        widget=forms.Select,
        choices=COIN_CHOICES
        )

    add_to_batch_command = forms.ChoiceField(
        label="Add to batch command",
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )
    
    confs = forms.IntegerField(
        label='Required swap confirmations',
        required=True,
        initial=3,
        min_value=1,
        max_value=5
        )

    nota = forms.ChoiceField(
        label='Requires swap notarisation',
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )

    tx_history = forms.ChoiceField(
        label='Preload transaction history',
        required=True,
        widget=forms.Select,
        choices=TF_CHOICES,
        initial=True
        )


class RecreateSwapDataForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    coin = forms.ChoiceField(
        label='Swap Coin',
        required=True,
        widget=forms.Select,
        choices=COIN_CHOICES
        )

    address = forms.CharField(
        label='Address',
        max_length=100,
        required=True
        )

    uuid =forms.CharField(
        label='Address',
        max_length=100,
        required=True
        )
