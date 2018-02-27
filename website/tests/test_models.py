from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone

from website.models import (Category, SubCategory, WebsiteRecommendation,
                            WebsiteComment, BookRecommendation, BookComment,
                            VideoRecommendation, VideoComment)
from django.contrib.auth.models import User


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name='Test Category',
                                category_img='https://www.test.com/')

    def test_category_name_label(self):
        category = Category.objects.get(name='Test Category')
        field_label = category._meta.get_field('name').verbose_name
        self.assertEquals(field_label,'name')

    def test_category_img_label(self):
        category = Category.objects.get(name='Test Category')
        field_label = category._meta.get_field('category_img').verbose_name
        self.assertEquals(field_label,'category img')

    def test_calling_category_returns_its_name(self):
        category = Category.objects.get(name='Test Category')
        name = category.name
        self.assertEquals(str(category), name)

    def test_slug_field(self):
        category = Category.objects.get(name='Test Category')
        self.assertEquals(category.slug, 'test-category')

    def test_name_max_length(self):
        category = Category.objects.get(name='Test Category')
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 128)


class SubcategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category',
            category_img='https://www.test.com/')
        category_2 = Category.objects.create(name='category_2',
            category_img='https://www.test2.com/')
        SubCategory.objects.create(name='Test Subcategory', category=category)

    def test_subcategory_name_label(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        field_label = subcategory._meta.get_field('name').verbose_name
        self.assertEquals(field_label,'name')

    def test_category_label(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        field_label = subcategory._meta.get_field('category').verbose_name
        self.assertEquals(field_label,'category')

    def test_subcategory_img_label(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        field_label = subcategory._meta.get_field('subcategory_img').verbose_name
        self.assertEquals(field_label,'subcategory img')

    def test_calling_subcategory_returns_its_name(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        name = subcategory.name
        self.assertEquals(str(subcategory), name)

    def test_slug_field(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        self.assertEquals(subcategory.slug, 'test-subcategory')

    def test_name_max_length(self):
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        max_length = subcategory._meta.get_field('name').max_length
        self.assertEquals(max_length, 128)

    def test_unique_together(self):
        # ensure you don't get duplicate subcategory names within the same
        # category.
        category = Category.objects.get(name='Test Category')
        with self.assertRaises(IntegrityError):
            SubCategory.objects.create(name='Test Subcategory',
                                       category=category)

    def test_ok_to_post_duplicate_subcategory_in_different_category(self):
        category = Category.objects.get(name='category_2')
        subcategory = SubCategory.objects.create(name='Test Subcategory 2',
                                                 category=category)
        self.assertEquals(subcategory.name, 'Test Subcategory 2')

class WebsiteRecommendationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        subcategory_2 = SubCategory.objects.create(name='subcategory_2',
                                                 category=category)
        # create test user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user3 = User.objects.create_user(username='testuser3',
                                              password='12345')
        test_user4 = User.objects.create_user(username='testuser4',
                                              password='12345')
        # create website
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=category,
            subcategory=subcategory,
            title='Test Website',
            description='test description',
            url='http://www.test.com'
        )
        website.upvote.add(test_user1,test_user2,test_user3)
        website.downvote.add(test_user4)

    def test_title_label(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        field_label = website._meta.get_field('title').verbose_name
        self.assertEquals(field_label,'title')

    def test_description_label(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        field_label = website._meta.get_field('description').verbose_name
        self.assertEquals(field_label,'description')

    def test_url_label(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        field_label = website._meta.get_field('url').verbose_name
        self.assertEquals(field_label,'url')

    def test_calling_WebsiteRecommendation_returns_its_title(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        title = website.title
        self.assertEquals(str(website), title)

    def test_title_max_length(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        max_length = website._meta.get_field('title').max_length
        self.assertEquals(max_length, 128)

    def test_description_max_length(self):
        website = WebsiteRecommendation.objects.get(title='Test Website')
        max_length = website._meta.get_field('description').max_length
        self.assertEquals(max_length, 300)

    def test_total_votes(self):
        # There are 3 upvotes and 1 downvote therefore should equal 2.
        website = WebsiteRecommendation.objects.get(title='Test Website')
        self.assertEquals(website.total_votes, 2)

    def test_unique_together(self):
        # ensure you don't get duplicate urls within a subcategory.
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        with self.assertRaises(IntegrityError):
            WebsiteRecommendation.objects.create(
                website_author=user,
                category=category,
                subcategory=subcategory,
                title='Test unique Website',
                description='test description',
                url='http://www.test.com'
            )

    def test_ok_to_post_duplicate_website_in_different_subcategory(self):
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory_2 = SubCategory.objects.get(name='subcategory_2')
        website = WebsiteRecommendation.objects.create(
            website_author=user,
            category=category,
            subcategory=subcategory_2,
            title='Test unique Website',
            description='test description',
            url='http://www.test.com'
        )
        self.assertEquals(website.url, 'http://www.test.com')

class WebsiteCommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        # create test user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create website
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=category,
            subcategory=subcategory,
            title='Test Website',
            description='test description',
            url='http://www.test.com'
        )
        # create comment
        comment = WebsiteComment.objects.create(
            website=website,
            author=test_user1,
            text='test comment'
        )

    def test_text_max_length(self):
        comment = WebsiteComment.objects.get(text='test comment')
        max_length = comment._meta.get_field('text').max_length
        self.assertEquals(max_length, 2000)

    def test_calling_WebsiteComment_returns_its_text(self):
        comment = WebsiteComment.objects.get(text='test comment')
        text = comment.text
        self.assertEquals(str(comment), text)

class BookRecommendationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        subcategory_2 = SubCategory.objects.create(name='subcategory_2',
                                                 category=category)
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user3 = User.objects.create_user(username='testuser3',
                                              password='12345')
        test_user4 = User.objects.create_user(username='testuser4',
                                              password='12345')
        # create book
        book = BookRecommendation.objects.create(
            isbn=1593276036,
            title='test title',
            recommended_by=test_user1,
            category=category,
            subcategory=subcategory,
            book_author='Test Author',
            book_description='Test Description',
            book_url='http://www.test.com',
            book_image_url='http://www.testimage.com',
            book_publish_date=timezone.now()
        )
        book.upvote.add(test_user1,test_user2,test_user3)
        book.downvote.add(test_user4)

    def test_isbn_label(self):
        book = BookRecommendation.objects.get(title='test title')
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEquals(field_label,'ISBN')

    def test_calling_BookRecommendation_returns_its_title(self):
        book = BookRecommendation.objects.get(title='test title')
        title = book.title
        self.assertEquals(str(book), title)

    def test_title_max_length(self):
        book = BookRecommendation.objects.get(title='test title')
        max_length = book._meta.get_field('title').max_length
        self.assertEquals(max_length, 500)

    def test_book_author_max_length(self):
        book = BookRecommendation.objects.get(title='test title')
        max_length = book._meta.get_field('book_author').max_length
        self.assertEquals(max_length, 128)

    def test_book_description_max_length(self):
        book = BookRecommendation.objects.get(title='test title')
        max_length = book._meta.get_field('book_description').max_length
        self.assertEquals(max_length, 10000)

    def test_book_url_max_length(self):
        book = BookRecommendation.objects.get(title='test title')
        max_length = book._meta.get_field('book_url').max_length
        self.assertEquals(max_length, 2000)

    def test_book_image_url_max_length(self):
        book = BookRecommendation.objects.get(title='test title')
        max_length = book._meta.get_field('book_image_url').max_length
        self.assertEquals(max_length, 500)

    def test_total_votes(self):
        # There are 3 upvotes and 1 downvote therefore should equal 2.
        book = BookRecommendation.objects.get(title='test title')
        self.assertEquals(book.total_votes, 2)

    def test_unique_together(self):
        # ensure you don't get duplicate ISBNS within a subcategory.
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        with self.assertRaises(IntegrityError):
            BookRecommendation.objects.create(
                isbn=1593276036,
                title='test title',
                recommended_by=user,
                category=category,
                subcategory=subcategory,
                book_author='Test Author',
                book_description='Test Description',
                book_url='http://www.test.com',
                book_image_url='http://www.testimage.com',
                book_publish_date=timezone.now()
            )

    def test_ok_to_post_duplicate_website_in_different_subcategory(self):
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory_2 = SubCategory.objects.get(name='subcategory_2')
        book = BookRecommendation.objects.create(
            isbn=1593276036,
            title='test title',
            recommended_by=user,
            category=category,
            subcategory=subcategory_2,
            book_author='Test Author',
            book_description='Test Description',
            book_url='http://www.test.com',
            book_image_url='http://www.testimage.com',
            book_publish_date=timezone.now()
        )
        self.assertEquals(book.isbn, 1593276036)

class BookCommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        # create test user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create book
        book = BookRecommendation.objects.create(
            isbn=1593276036,
            title='test title',
            recommended_by=test_user1,
            category=category,
            subcategory=subcategory,
            book_author='Test Author',
            book_description='Test Description',
            book_url='http://www.test.com',
            book_image_url='http://www.testimage.com',
            book_publish_date=timezone.now()
        )
        # create comment
        comment = BookComment.objects.create(
            book=book,
            author=test_user1,
            text='test comment'
        )

    def test_text_max_length(self):
        comment = BookComment.objects.get(text='test comment')
        max_length = comment._meta.get_field('text').max_length
        self.assertEquals(max_length, 2000)

    def test_calling_BookComment_returns_its_text(self):
        comment = BookComment.objects.get(text='test comment')
        text = comment.text
        self.assertEquals(str(comment), text)

class VideoRecommendationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        subcategory_2 = SubCategory.objects.create(name='subcategory_2',
                                                 category=category)
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user3 = User.objects.create_user(username='testuser3',
                                              password='12345')
        test_user4 = User.objects.create_user(username='testuser4',
                                              password='12345')
        # create video
        video = VideoRecommendation.objects.create(
            title='test title',
            recommended_by=test_user1,
            category=category,
            subcategory=subcategory,
            video_description='Test Description',
            video_publish_date=timezone.now(),
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            video_image_url='https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg',
            video_id='dQw4w9WgXcQ',
        )
        video.upvote.add(test_user1,test_user2,test_user3)
        video.downvote.add(test_user4)

    def test_video_url_label(self):
        video = VideoRecommendation.objects.get(title='test title')
        field_label = video._meta.get_field('video_url').verbose_name
        self.assertEquals(field_label,'video url')

    def test_calling_VideoRecommendation_returns_its_title(self):
        video = VideoRecommendation.objects.get(title='test title')
        title = video.title
        self.assertEquals(str(video), title)

    def test_title_max_length(self):
        video = VideoRecommendation.objects.get(title='test title')
        max_length = video._meta.get_field('title').max_length
        self.assertEquals(max_length, 128)

    def test_video_description_max_length(self):
        video = VideoRecommendation.objects.get(title='test title')
        max_length = video._meta.get_field('video_description').max_length
        self.assertEquals(max_length, 10000)

    def test_video_url_max_length(self):
        video = VideoRecommendation.objects.get(title='test title')
        max_length = video._meta.get_field('video_url').max_length
        self.assertEquals(max_length, 2000)

    def test_video_image_url_max_length(self):
        video = VideoRecommendation.objects.get(title='test title')
        max_length = video._meta.get_field('video_image_url').max_length
        self.assertEquals(max_length, 500)

    def test_video_id_max_length(self):
        video = VideoRecommendation.objects.get(title='test title')
        max_length = video._meta.get_field('video_id').max_length
        self.assertEquals(max_length, 128)

    def test_total_votes(self):
        # There are 3 upvotes and 1 downvote therefore should equal 2.
        video = VideoRecommendation.objects.get(title='test title')
        self.assertEquals(video.total_votes, 2)

    def test_unique_together(self):
        # ensure you don't get duplicate videos within a subcategory.
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory = SubCategory.objects.get(name='Test Subcategory')
        with self.assertRaises(IntegrityError):
            VideoRecommendation.objects.create(
                title='test title',
                recommended_by=user,
                category=category,
                subcategory=subcategory,
                video_description='Test Description',
                video_publish_date=timezone.now(),
                video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                video_image_url='https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg',
                video_id='dQw4w9WgXcQ',
            )

    def test_ok_to_post_duplicate_website_in_different_subcategory(self):
        user = User.objects.get(username='testuser3')
        category = Category.objects.get(name='Test Category')
        subcategory_2 = SubCategory.objects.get(name='subcategory_2')
        video = VideoRecommendation.objects.create(
            title='test title',
            recommended_by=user,
            category=category,
            subcategory=subcategory_2,
            video_description='Test Description',
            video_publish_date=timezone.now(),
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            video_image_url='https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg',
            video_id='dQw4w9WgXcQ',
        )
        self.assertEquals(video.video_id, 'dQw4w9WgXcQ')

class VideoCommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category')
        subcategory = SubCategory.objects.create(name='Test Subcategory',
                                                 category=category)
        # create test user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        # create video
        video = VideoRecommendation.objects.create(
            title='test title',
            recommended_by=test_user1,
            category=category,
            subcategory=subcategory,
            video_description='Test Description',
            video_publish_date=timezone.now(),
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            video_image_url='https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg',
            video_id='dQw4w9WgXcQ',
        )
        # create comment
        comment = VideoComment.objects.create(
            video=video,
            author=test_user1,
            text='test comment'
        )

    def test_text_max_length(self):
        comment = VideoComment.objects.get(text='test comment')
        max_length = comment._meta.get_field('text').max_length
        self.assertEquals(max_length, 2000)

    def test_calling_VideoComment_returns_its_text(self):
        comment = VideoComment.objects.get(text='test comment')
        text = comment.text
        self.assertEquals(str(comment), text)
