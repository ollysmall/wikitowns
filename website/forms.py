from django import forms
from website.models import WebsiteRecommendation, WebsiteComment, BookRecommendation, BookComment


class WebsiteForm(forms.ModelForm):

    url = forms.URLField(max_length=200, initial='http://')

    class Meta:
        model = WebsiteRecommendation
        fields = ('title', 'description', 'url')

class WebsiteCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = WebsiteComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }

class BookForm(forms.ModelForm):

    class Meta:
        model = BookRecommendation
        fields = ('isbn', )

class BookCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = BookComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }
