from django.test import TestCase

from website.models import (Category, SubCategory, WebsiteRecommendation,
                            BookRecommendation, VideoRecommendation)
from website.forms import (WebsiteForm, WebsiteCommentForm, BookForm,
                           BookCommentForm, VideoForm, VideoCommentForm)
from django.utils import timezone
from django.contrib.auth.models import User

class WebsiteFormTest(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create test category
        test_category1 = Category.objects.create(name='python')
        # create test subcategories
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        test_subcategory2 = SubCategory.objects.create(name='flask',
                                                       category=test_category1)
        # create website to test unique url form validation
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='https://www.test.com/',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

    def test_website_form_title_field_label(self):
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form = WebsiteForm(category=category, subcategory=subcategory)
        self.assertTrue(form.fields['title'].label == None or
                        form.fields['title'].label == 'Title')

    def test_website_form_description_field_label(self):
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form = WebsiteForm(category=category, subcategory=subcategory)
        self.assertTrue(form.fields['description'].label == None or
                        form.fields['description'].label == 'Description')

    def test_website_form_url_field_label(self):
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form = WebsiteForm(category=category, subcategory=subcategory)
        self.assertTrue(form.fields['url'].label == None or
                        form.fields['url'].label == 'Url')

    def test_website_form_does_not_allow_duplicate_urls(self):
        # the same url cannot be recommended twice within the same subcategory
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'title': 'test', 'description': 'test description',
                     'url': 'https://www.test.com/'}
        form = WebsiteForm(data=form_data, category=category,
                           subcategory=subcategory)
        self.assertFalse(form.is_valid())

    def test_website_form_allows_same_url_in_different_subcategories(self):
        # the same url can be recommended within differnet subcategories
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='flask')
        form_data = {'title': 'test', 'description': 'test description',
                     'url': 'https://www.test.com/'}
        form = WebsiteForm(data=form_data, category=category,
                           subcategory=subcategory)
        self.assertTrue(form.is_valid())


class WebsiteCommentFormTest(TestCase):

    def test_website_comment_form_text_field_label(self):
        form = WebsiteCommentForm()
        self.assertTrue(form.fields['text'].label == None or
                        form.fields['text'].label == '')


class BookFormTest(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create test category
        test_category1 = Category.objects.create(name='python')
        # create test subcategories
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        test_subcategory2 = SubCategory.objects.create(name='flask',
                                                       category=test_category1)
        # create book to test unique isnb form validation
        book = BookRecommendation.objects.create(
            isbn=1593276036,
            title='test title',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='Test Author',
            book_description='Test Description',
            book_url='http://www.test.com',
            book_image_url='http://www.testimage.com',
            book_publish_date=timezone.now()
        )

    def test_book_form_isbn_field_label(self):
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form = BookForm(category=category, subcategory=subcategory)
        self.assertTrue(form.fields['isbn'].label == None or
                        form.fields['isbn'].label == 'ISBN')

    def test_book_form_does_not_allow_duplicate_isbns(self):
        # the same isbn cannot be recommended twice within the same subcategory
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'isbn': 1593276036}
        form = BookForm(data=form_data, category=category,
                           subcategory=subcategory)
        self.assertFalse(form.is_valid())

    def test_book_form_allows_same_isbn_in_different_subcategories(self):
        # the same isbn can be recommended within differnet subcategories
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='flask')
        form_data = {'isbn': 1593276036}
        form = BookForm(data=form_data, category=category,
                           subcategory=subcategory)
        self.assertTrue(form.is_valid())

class BookCommentFormTest(TestCase):

    def test_book_comment_form_text_field_label(self):
        form = BookCommentForm()
        self.assertTrue(form.fields['text'].label == None or
                        form.fields['text'].label == '')

class VideoFormTest(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create test category
        test_category1 = Category.objects.create(name='python')
        # create test subcategories
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        test_subcategory2 = SubCategory.objects.create(name='flask',
                                                       category=test_category1)
        # create video to test unique video id form validation
        video = VideoRecommendation.objects.create(
            title='test title',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description='Test Description',
            video_publish_date=timezone.now(),
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            video_image_url='https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg',
            video_id='dQw4w9WgXcQ',
        )

    def test_video_form_url_field_label(self):
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form = VideoForm(category=category, subcategory=subcategory)
        self.assertTrue(form.fields['video_url'].label == None or
                        form.fields['video_url'].label == 'Video url')

    def test_video_form_does_not_allow_duplicate_video_ids(self):
        # the same id cannot be recommended twice within the same subcategory
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'video_url':'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        form = VideoForm(data=form_data, category=category,
                         subcategory=subcategory)
        self.assertFalse(form.is_valid())

    def test_video_form_allows_same_video_id_in_different_subcategories(self):
        # the same id can be recommended within differnet subcategories
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='flask')
        form_data = {'video_url':'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        form = VideoForm(data=form_data, category=category,
                         subcategory=subcategory)
        self.assertTrue(form.is_valid())

    def test_video_form_does_not_allow_youtube_url_without_id(self):
        # ensure the form is invalid if a youtube link is supplied without
        # an id
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'video_url':'https://www.youtube.com/'}
        form = VideoForm(data=form_data, category=category,
                         subcategory=subcategory)
        self.assertFalse(form.is_valid())

    def test_video_form_does_not_allow_small_youtube_url_without_id(self):
        # ensure the form is invalid if a youtube link is supplied without
        # an id
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'video_url':'https://www.youtu.be'}
        form = VideoForm(data=form_data, category=category,
                         subcategory=subcategory)
        self.assertFalse(form.is_valid())

    def test_video_form_does_not_allow_url_which_is_not_youtube(self):
        # ensure the form is invalid if a url other than youtube is supplied
        category = Category.objects.get(name='python')
        subcategory = SubCategory.objects.get(name='django')
        form_data = {'video_url':'https://vimeo.com/250231574'}
        form = VideoForm(data=form_data, category=category,
                         subcategory=subcategory)
        self.assertFalse(form.is_valid())

class VideoCommentFormTest(TestCase):

    def test_video_comment_form_text_field_label(self):
        form = VideoCommentForm()
        self.assertTrue(form.fields['text'].label == None or
                        form.fields['text'].label == '')
