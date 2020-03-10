from django import forms
from django_countries.fields import CountryField

choices = (
    ('s', 'stripe'),
    ('b', 'bikash'),
    ('r', 'rocket'),
)


class CheckOutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Road No...'}))
    appartment_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Apartment or Suite', 'class': 'col-md-12 form-control'}))
    country = CountryField(blank_label="Select country").formfield()
    zip = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'col-md-6 form-control'}))
    same_billing_address = forms.BooleanField()
    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=choices, required=False)


class CouponForm(forms.Form):
    coupon = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Add coupon',
            'class': 'form-control',


        }))
