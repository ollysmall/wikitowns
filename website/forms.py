from django import forms
from website.models import WebsiteRecommendation, WebsiteComment, BookRecommendation, BookComment, VideoRecommendation, VideoComment
from registration.forms import RegistrationForm

from urllib.parse import urlparse, parse_qs

#this allows bootstrap classes to be used on the registration form
class MyCustomRegistrationForm(RegistrationForm):

    def __init__(self, *args, **kwargs):
        super(MyCustomRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'maxlength': 30})
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

class WebsiteForm(forms.ModelForm):

    url = forms.URLField(max_length=200, widget=forms.TextInput( attrs={ 'class': 'form-control', 'required': True, } ))

    class Meta:
        model = WebsiteRecommendation
        fields = ('title', 'description', 'url')
        widgets = {
            'title': forms.TextInput( attrs={ 'class': 'form-control', 'required': True, 'autofocus':'autofocus', } ),
            'description': forms.Textarea( attrs={'cols': 30, 'rows': 4, 'class': 'form-control', 'required': True, } ),
        }

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        self.subcategory = kwargs.pop('subcategory')
        print(self.category)
        super(WebsiteForm, self).__init__(*args, **kwargs)

    def clean_url(self):
        url = self.cleaned_data['url']

        if WebsiteRecommendation.objects.filter(url=url, category=self.category, subcategory=self.subcategory).exists():
            raise forms.ValidationError("This website has already been recommended!")

        return url


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
            'isbn': forms.TextInput( attrs={ 'class': 'form-control', 'required': True, 'autofocus':'autofocus', } ),
        }

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        self.subcategory = kwargs.pop('subcategory')
        super(BookForm, self).__init__(*args, **kwargs)

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']

        if BookRecommendation.objects.filter(isbn=isbn, category=self.category, subcategory=self.subcategory).exists():
            raise forms.ValidationError("This book has already been recommended!")

        return isbn

class BookCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = BookComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }

class VideoForm(forms.ModelForm):

    video_url = forms.URLField(max_length=200, widget=forms.TextInput( attrs={ 'class': 'form-control', 'required': True, 'autofocus':'autofocus', } ))

    class Meta:
        model = VideoRecommendation
        fields = ('video_url', )

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        self.subcategory = kwargs.pop('subcategory')
        super(VideoForm, self).__init__(*args, **kwargs)

    def clean_video_url(self):
        url = self.cleaned_data['video_url']
        query = urlparse(url)

        if 'youtube' in query.hostname:
            if query.path == '/watch':
                video_id= parse_qs(query.query)['v'][0]
            elif query.path.startswith(('/embed/', '/v/')):
                video_id= query.path.split('/')[2]
            else:raise forms.ValidationError("Please make sure the YouTube link is correct and has the video id included!")

        elif 'youtu.be' in query.hostname:
            #to stop empty url being posted - check query has 11 characters for id
            if len(query.path[1:]) >= 11:
                video_id= query.path[1:]
            else:
                raise forms.ValidationError("Please make sure the link includes the correct video ID number!")

        else:
            print(query)
            raise forms.ValidationError("Please make sure the video you are recommending is from YouTube!")

        if VideoRecommendation.objects.filter(video_id=video_id, category=self.category, subcategory=self.subcategory).exists():
            raise forms.ValidationError("This video has already been recommended!")

        return url

class VideoCommentForm(forms.ModelForm):

    text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 2, 'class': 'comment-textbox, form-control', 'placeholder': ' Write a comment...'}))

    class Meta:
        model = VideoComment
        fields = ('text',)
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':30, 'class': 'comment-textbox'}),
        }

class DateFilterForm(forms.Form):

    CHOICES = (('all-time-best','All time best'),
               ('best-of-year','Best of year'),
               ('best-of-month','Best of month'),
               ('newest','Newest'),)

    time_filter = forms.ChoiceField(
        required=False,
        label='',
        widget=forms.Select(attrs={'onchange': 'form.submit();', 'class': 'form-control-sm custom-select',}),
        choices=CHOICES)
