from django import forms
from website.models import WebsiteRecommendation

class WebsiteForm(forms.ModelForm):

    url = forms.URLField(max_length=200, initial='http://')

    class Meta:
        model = WebsiteRecommendation
        fields = ('title', 'description', 'url')
