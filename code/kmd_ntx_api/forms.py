from django import forms

from kmd_ntx_api.info import get_mm2_coins_list

TF_CHOICES = [(True,True), (False,False)]
COIN_CHOICES = [(i,i) for i in get_mm2_coins_list()]

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
