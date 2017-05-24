from django import forms
from website.models import WebsiteRecommendation, WebsiteComment, BookRecommendation, BookComment, VideoRecommendation, VideoComment


class WebsiteForm(forms.ModelForm):

    url = forms.URLField(max_length=200, initial='http://', widget=forms.TextInput( attrs={ 'class': 'form-control', 'required': True, } ))

    class Meta:
        model = WebsiteRecommendation
        fields = ('title', 'description', 'url')
        widgets = {
            'title': forms.TextInput( attrs={ 'class': 'form-control', 'required': True, } ),
            'description': forms.Textarea( attrs={'cols': 30, 'rows': 4, 'class': 'form-control', 'required': True, } ),
        }


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
        fields = ('isbn',)
        widgets = {
            'isbn': forms.TextInput( attrs={ 'class': 'form-control', 'required': True, } ),
        }

class BookCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = BookComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }

class VideoForm(forms.ModelForm):

    video_url = forms.URLField(max_length=200, initial='http://', widget=forms.TextInput( attrs={ 'class': 'form-control', 'required': True, } ))

    class Meta:
        model = VideoRecommendation
        fields = ('video_url', )

class VideoCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = VideoComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }
