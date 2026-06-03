from django import forms
from .models import AffiliateLink

class AffiliateLinkForm(forms.ModelForm):
    class Meta:
        model = AffiliateLink
        fields = []