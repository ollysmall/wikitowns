from django.test import TestCase, TransactionTestCase

from website.models import (Category, SubCategory, WebsiteRecommendation,
                            BookRecommendation, VideoRecommendation,
                            WebsiteComment, BookComment, VideoComment)
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime
from django.core import mail


class IndexViewTests(TestCase):

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/index.html')

    def test_lists_all_categories(self):
        # create 9 categories to test against
        number_of_categories = 9
        for category_num in range(number_of_categories):
            Category.objects.create(
                name='category %s' % category_num,
                category_img='www.test%s.com' % category_num
            )

        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['categories']), 9)

    def test_empty_category_list(self):
        # if no categories exist an appropriate error message should show
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['categories']), 0)
        self.assertContains(resp, "There are no categories listed.")


class CategoryViewTests(TestCase):

    def setUp(self):
        # create 2 test categories, one will have subcategories and the
        # other wont.
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        test_category2 = Category.objects.create(name='ruby')
        test_category2.save()
        # create 3 test subcategories all linked to category named python.
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        test_subcategory1.save()
        test_subcategory2 = SubCategory.objects.create(name='flask',
                                                       category=test_category1)
        test_subcategory2.save()
        test_subcategory3 = SubCategory.objects.create(name='pyramid',
                                                       category=test_category1)
        test_subcategory3.save()

    def test_view_url_accessible_by_name(self):
        test_category1 = Category.objects.get(name='python')
        url = reverse('category', args=(test_category1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        test_category1 = Category.objects.get(name='python')
        url = reverse('category', args=(test_category1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/category.html')

    def test_category_url_that_does_not_exist(self):
        # if a category is manually typed into the url an appropriate
        # error message should be shown if it does not exist.
        url = reverse('category', args=('test',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_lists_all_categories(self):
        # test categories context is being passed
        test_category1 = Category.objects.get(name='python')
        url = reverse('category', args=(test_category1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['categories']), 2)

    def test_lists_all_subcategories(self):
        # test subcategories context is being passed
        test_category1 = Category.objects.get(name='python')
        url = reverse('category', args=(test_category1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['subcategories']), 3)

    def test_empty_subcategory_list(self):
        # if no categories exist an appropriate error message should show
        test_category2 = Category.objects.get(name='ruby')
        url = reverse('category', args=(test_category2.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['subcategories']), 0)
        self.assertContains(resp, "No subcategory currently in category.")

    def test_category_title_is_shown(self):
        test_category1 = Category.objects.get(name='python')
        url = reverse('category', args=(test_category1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "python")

class SubCategoryViewTests(TestCase):

    def setUp(self):
        # create 4 users - needed for upvotes
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        test_user3 = User.objects.create_user(username='testuser3',
                                              password='12345')
        test_user3.save()
        test_user4 = User.objects.create_user(username='testuser4',
                                              password='12345')
        test_user4.save()
        # create test categories
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        test_category2 = Category.objects.create(name='ruby')
        test_category2.save()
        # create 2 test subcategories with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        test_subcategory2 = SubCategory.objects.create(name='flask',
                                                       category=test_category1)
        # create test subcategory with different category
        test_subcategory3 = SubCategory.objects.create(name='ruby on rails',
                                                       category=test_category2)
        # create 5 websites all in the same subcategory

        today = timezone.now()

        test_website1 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website1',
            description='test description 1',
            url='www.testurl1.com',
            image_url='www.testimageurl1.com',
            created_date=today,
        )
        # add upvotes
        test_website1.upvote.add(test_user1)

        test_website2 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website2',
            description='test description 2',
            url='www.testurl2.com',
            image_url='www.testimageurl2.com',
            created_date=today - timezone.timedelta(weeks=5)
        )
        # add upvotes
        test_website2.upvote.add(test_user1, test_user2, test_user3)

        test_website3 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website3',
            description='test description 3',
            url='www.testurl3.com',
            image_url='www.testimageurl3.com',
            created_date=today - timezone.timedelta(weeks=60)
        )
        # add upvotes
        test_website3.upvote.add(test_user1, test_user2)

        test_website4 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website4',
            description='test description 4',
            url='www.testurl4.com',
            image_url='www.testimageurl4.com',
            created_date=today
        )
        # add upvotes
        test_website4.upvote.add(test_user1, test_user2, test_user3,
                                 test_user4)

        test_website5 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website5',
            description='test description 5',
            url='www.testurl5.com',
            image_url='www.testimageurl5.com',
            created_date=today
        )

        # create 1 website in same category as websites above but different
        # subcategory in order to test filtering
        WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory2,
            title='test_website6',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
        )
        # create 1 website in different category as websites above and different
        # subcategory in order to test filtering
        WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category2,
            subcategory=test_subcategory3,
            title='test website with different category and subcategory',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
        )

        # create 5 books all in the same subcategory
        test_book1 = BookRecommendation.objects.create(
            isbn=1449340377,
            title='test_book1',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='test_book_author1',
            book_description='book description',
            book_url='www.testurl1.com',
            book_image_url='www.testimageurl1.com',
            book_publish_date=today,
            created_date=today
        )
        # add upvotes
        test_book1.upvote.add(test_user1)

        test_book2 = BookRecommendation.objects.create(
            isbn=1491912057,
            title='test_book2',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='test_book_author2',
            book_description='book description',
            book_url='www.testurl2.com',
            book_image_url='www.testimageurl2.com',
            book_publish_date=today,
            created_date=today - timezone.timedelta(weeks=5)
        )
        # add upvotes
        test_book2.upvote.add(test_user1, test_user2, test_user3)

        test_book3 = BookRecommendation.objects.create(
            isbn=1491933178,
            title='test_book3',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='test_book_author3',
            book_description='book description',
            book_url='www.testurl3.com',
            book_image_url='www.testimageurl3.com',
            book_publish_date=today,
            created_date=today - timezone.timedelta(weeks=60)
        )
        # add upvotes
        test_book3.upvote.add(test_user1, test_user2)

        test_book4 = BookRecommendation.objects.create(
            isbn=1785881116,
            title='test_book4',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='test_book_author4',
            book_description='book description',
            book_url='www.testurl4.com',
            book_image_url='www.testimageurl4.com',
            book_publish_date=today,
            created_date=today
        )
        # add upvotes
        test_book4.upvote.add(test_user1, test_user2, test_user3,
                                 test_user4)

        test_book5 = BookRecommendation.objects.create(
            isbn=1784391913,
            title='test_book5',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            book_author='test_book_author5',
            book_description='book description',
            book_url='www.testurl5.com',
            book_image_url='www.testimageurl5.com',
            book_publish_date=today,
            created_date=today
        )
        # create 1 book in same category as books above but different
        # subcategory in order to test filtering
        BookRecommendation.objects.create(
            isbn=1449372627,
            title='test book with different subcategory',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory2,
            book_author='James Brown',
            book_description='book description',
            book_url='www.testurl.com',
            book_image_url='www.testimageurl.com',
            book_publish_date=timezone.now()
        )
        # create 1 book in different category as books above and different
        # subcategory in order to test filtering
        BookRecommendation.objects.create(
            isbn=1593276036,
            title='test book with different category and subcategory',
            recommended_by=test_user1,
            category=test_category2,
            subcategory=test_subcategory3,
            book_author='Harry Potter',
            book_description='book description',
            book_url='www.testurl.com',
            book_image_url='www.testimageurl.com',
            book_publish_date=timezone.now()
        )

        # create 5 videos all in the same category and subcategory
        test_video1 = VideoRecommendation.objects.create(
            title='test_video1',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description = 'video description',
            video_publish_date = today,
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 1234,
            created_date=today
        )
        # add upvotes
        test_video1.upvote.add(test_user1)

        test_video2 = VideoRecommendation.objects.create(
            title='test_video2',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description = 'video description',
            video_publish_date = today,
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 1235,
            created_date=today - timezone.timedelta(weeks=5)
        )
        # add upvotes
        test_video2.upvote.add(test_user1, test_user2, test_user3)

        test_video3 = VideoRecommendation.objects.create(
            title='test_video3',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description = 'video description',
            video_publish_date = today,
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 1236,
            created_date=today - timezone.timedelta(weeks=60)
        )
        # add upvotes
        test_video3.upvote.add(test_user1, test_user2)

        test_video4 = VideoRecommendation.objects.create(
            title='test_video4',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description = 'video description',
            video_publish_date = today,
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 1237,
            created_date=today
        )
        # add upvotes
        test_video4.upvote.add(test_user1, test_user2, test_user3,
                               test_user4)

        test_video5 = VideoRecommendation.objects.create(
            title='test_video5',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            video_description = 'video description',
            video_publish_date = today,
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 1238,
            created_date=today
        )

        # create 1 book in same category as books above but different
        # subcategory in order to test filtering
        VideoRecommendation.objects.create(
            title='test video with different subcategory',
            recommended_by=test_user1,
            category=test_category1,
            subcategory=test_subcategory2,
            video_description = 'video description',
            video_publish_date = timezone.now(),
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 23456,
        )
        # create 1 book in different category as books above and different
        # subcategory in order to test filtering
        VideoRecommendation.objects.create(
            title='test video with different category and subcategory',
            recommended_by=test_user1,
            category=test_category2,
            subcategory=test_subcategory3,
            video_description = 'video description',
            video_publish_date = timezone.now(),
            video_url = 'www.testurl.com',
            video_image_url = 'www.testimageurl.com',
            video_id = 34567,
        )

    def test_view_url_accessible_by_name(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('subcategory', args=(test_category1.slug,
                                           test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('subcategory', args=(test_category1.slug,
                                           test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/subcategory.html')

    def test_subcategory_url_that_does_not_exist(self):
        # if a subcategory is manually typed into the url an appropriate
        # error message should be shown if it does not exist.
        url = reverse('subcategory', args=('python', 'test',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_subcategory_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url an appropriate
        # error message should be shown if it does not exist.
        url = reverse('subcategory', args=('test', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_lists_all_websites_in_subcategory(self):
        # test websites context is being passed
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['websites']), 5)

    def test_filtering_of_websites_by_subcategory(self):
        # test websites are filtered correcty by subcategory
        url = reverse('subcategory', args=('python', 'flask',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['websites']), 1)
        self.assertContains(resp, "test_website6")

    def test_filtering_of_websites_by_category_and_subcategory(self):
        # test websites are filtered correcty by category and subcategory
        test_subcategory = SubCategory.objects.get(name='ruby on rails')
        url = reverse('subcategory', args=('ruby', test_subcategory.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['websites']), 1)
        self.assertContains(
            resp, "test website with different category and subcategory")

    def test_lists_all_books_in_subcategory(self):
        # test books context is being passed
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['books']), 5)

    def test_filtering_of_books_by_subcategory(self):
        # test books are filtered correcty by subcategory
        url = reverse('subcategory', args=('python', 'flask',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['books']), 1)
        self.assertContains(resp, "test book with different subcategory")

    def test_filtering_of_books_by_category_and_subcategory(self):
        # test books are filtered correcty by category and subcategory
        test_subcategory = SubCategory.objects.get(name='ruby on rails')
        url = reverse('subcategory', args=('ruby', test_subcategory.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['books']), 1)
        self.assertContains(
            resp, "test book with different category and subcategory")

    def test_lists_all_videos_in_subcategory(self):
        # test videos context is being passed
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['videos']), 5)

    def test_filtering_of_videos_by_subcategory(self):
        # test videos are filtered correcty by subcategory
        url = reverse('subcategory', args=('python', 'flask',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['videos']), 1)
        self.assertContains(resp, "test video with different subcategory")

    def test_filtering_of_videos_by_category_and_subcategory(self):
        # test videos are filtered correcty by category and subcategory
        test_subcategory = SubCategory.objects.get(name='ruby on rails')
        url = reverse('subcategory', args=('ruby', test_subcategory.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['videos']), 1)
        self.assertContains(
            resp, "test video with different category and subcategory")

    def test_standard_ordering_of_websites_is_by_votes(self):
        # the standard ordering should be by all time best with the websites
        # with the most votes at the top of the page and the lowest at the
        # bottom
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        websites = resp.context['websites']
        count = 0
        # correct order that the websites should be in due to upvotes
        website_list = ['test_website4', 'test_website2', 'test_website3',
                        'test_website1', 'test_website5']
        for website in websites:
            self.assertEqual(website.title, website_list[count])
            count += 1

    def test_best_of_year_ordering_of_websites(self):
        # best of year ordering of websites should only show websites
        # recommended that year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-year'
            )
        self.assertEqual(resp.status_code, 200)
        websites = resp.context['websites']
        website_upvote_total = 10
        for website in websites:
            # check context websites have the same year as the year we are in
            # today
            self.assertEqual(website.created_date.year, timezone.now().year)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(website.upvote.count(), website_upvote_total)
            website_upvote_total = website.upvote.count()

    def test_best_of_month_ordering_of_websites(self):
        # best of month ordering of websites should only show websites
        # recommended in that month and year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-month'
            )
        self.assertEqual(resp.status_code, 200)
        websites = resp.context['websites']
        website_upvote_total = 10
        for website in websites:
            # check context websites have the same year as the year we are in
            # today
            self.assertEqual(website.created_date.year, timezone.now().year)
            # check context websites have the same month as the year we are in
            # today
            self.assertEqual(website.created_date.month, timezone.now().month)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(website.upvote.count(), website_upvote_total)
            website_upvote_total = website.upvote.count()


    def test_newest_ordering_of_websites(self):
        # order by newest should only order by newest date first. There is
        # no ordering by votes.
        resp = self.client.get('/category/python/django/?time_filter=newest')
        self.assertEqual(resp.status_code, 200)
        websites = resp.context['websites']
        date = timezone.now()
        for website in websites:
            self.assertLessEqual(website.created_date, date)
            date = website.created_date

    def test_standard_ordering_of_books_is_by_votes(self):
        # the standard ordering should be by all time best with the books
        # with the most votes at the top of the page and the lowest at the
        # bottom
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        books = resp.context['books']
        count = 0
        # correct order that the websites should be in due to upvotes
        book_list = ['test_book4', 'test_book2', 'test_book3',
                        'test_book1', 'test_book5']
        for book in books:
            self.assertEqual(book.title, book_list[count])
            count += 1

    def test_best_of_year_ordering_of_books(self):
        # best of year ordering of books should only show books
        # recommended that year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-year'
            )
        self.assertEqual(resp.status_code, 200)
        books = resp.context['books']
        book_upvote_total = 10
        for book in books:
            # check context books have the same year as the year we are in
            # today
            self.assertEqual(book.created_date.year, timezone.now().year)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(book.upvote.count(), book_upvote_total)
            book_upvote_total = book.upvote.count()

    def test_best_of_month_ordering_of_books(self):
        # best of month ordering of books should only show books
        # recommended in that month and year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-month'
            )
        self.assertEqual(resp.status_code, 200)
        books = resp.context['books']
        book_upvote_total = 10
        for book in books:
            # check context books have the same year as the year we are in
            # today
            self.assertEqual(book.created_date.year, timezone.now().year)
            # check context books have the same month as the year we are in
            # today
            self.assertEqual(book.created_date.month, timezone.now().month)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(book.upvote.count(), book_upvote_total)
            book_upvote_total = book.upvote.count()

    def test_newest_ordering_of_books(self):
        # order by newest should only order by newest date first. There is
        # no ordering by votes.
        resp = self.client.get('/category/python/django/?time_filter=newest')
        self.assertEqual(resp.status_code, 200)
        books = resp.context['books']
        date = timezone.now()
        for book in books:
            self.assertLessEqual(book.created_date, date)
            date = book.created_date

    def test_standard_ordering_of_videos_is_by_votes(self):
        # the standard ordering should be by all time best with the videos
        # with the most votes at the top of the page and the lowest at the
        # bottom
        url = reverse('subcategory', args=('python', 'django',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        videos = resp.context['videos']
        count = 0
        # correct order that the websites should be in due to upvotes
        video_list = ['test_video4', 'test_video2', 'test_video3',
                        'test_video1', 'test_video5']
        for video in videos:
            self.assertEqual(video.title, video_list[count])
            count += 1

    def test_best_of_year_ordering_of_videos(self):
        # best of year ordering of books should only show videos
        # recommended that year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-year'
            )
        self.assertEqual(resp.status_code, 200)
        videos = resp.context['videos']
        video_upvote_total = 10
        for video in videos:
            # check context videos have the same year as the year we are in
            # today
            self.assertEqual(video.created_date.year, timezone.now().year)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(video.upvote.count(), video_upvote_total)
            video_upvote_total = video.upvote.count()

    def test_best_of_month_ordering_of_videos(self):
        # best of month ordering of videos should only show videos
        # recommended in that month and year and in highest votes order

        resp = self.client.get(
            '/category/python/django/?time_filter=best-of-month'
            )
        self.assertEqual(resp.status_code, 200)
        videos = resp.context['videos']
        video_upvote_total = 10
        for video in videos:
            # check context videos have the same year as the year we are in
            # today
            self.assertEqual(video.created_date.year, timezone.now().year)
            # check context videos have the same month as the year we are in
            # today
            self.assertEqual(video.created_date.month, timezone.now().month)
            # check the order of votes - should be highest to lowest
            self.assertLessEqual(video.upvote.count(), video_upvote_total)
            video_upvote_total = video.upvote.count()

    def test_newest_ordering_of_videos(self):
        # order by newest should only order by newest date first. There is
        # no ordering by votes.
        resp = self.client.get('/category/python/django/?time_filter=newest')
        self.assertEqual(resp.status_code, 200)
        videos = resp.context['videos']
        date = timezone.now()
        for video in videos:
            self.assertLessEqual(video.created_date, date)
            date = video.created_date

    def test_search_keywords_are_being_passed_into_context(self):
        resp = self.client.get('/category/python/django/?search_box=test')
        self.assertEqual(resp.status_code, 200)
        search_keywords = resp.context['search_keywords']
        self.assertEqual(resp.context['search_keywords'], 'test')

    def test_search_bar_works_with_websites(self):
        resp = self.client.get(
            '/category/python/django/?search_box=test_website1'
        )
        self.assertEqual(resp.status_code, 200)
        # it should only return one item
        self.assertEqual(len(resp.context['websites']), 1)
        # check the search has found the correct website
        websites = resp.context['websites']
        for website in websites:
            self.assertEqual(website.title, 'test_website1')
        # check that the books and videos tabs display a message saying
        # nothing had been found
        self.assertContains(
            resp, 'No books matched your search - "test_website1"'
        )
        self.assertEqual(len(resp.context['books']), 0)
        self.assertContains(
            resp, 'No videos matched your search - "test_website1"'
        )
        self.assertEqual(len(resp.context['videos']), 0)

    def test_search_bar_works_with_books(self):
        resp = self.client.get(
            '/category/python/django/?search_box=test_book1'
        )
        self.assertEqual(resp.status_code, 200)
        # it should only return one item
        self.assertEqual(len(resp.context['books']), 1)
        # check the search has found the correct book
        books = resp.context['books']
        for book in books:
            self.assertEqual(book.title, 'test_book1')
        # check that the websites and videos tabs display a message saying
        # nothing had been found and contexts are empty
        self.assertContains(
            resp, 'No websites matched your search - "test_book1"'
        )
        self.assertEqual(len(resp.context['websites']), 0)
        self.assertContains(
            resp, 'No videos matched your search - "test_book1"'
        )
        self.assertEqual(len(resp.context['videos']), 0)

    def test_search_bar_works_with_videos(self):
        resp = self.client.get(
            '/category/python/django/?search_box=test_video1'
        )
        self.assertEqual(resp.status_code, 200)
        # it should only return one item
        self.assertEqual(len(resp.context['videos']), 1)
        # check the search has found the correct video
        videos = resp.context['videos']
        for video in videos:
            self.assertEqual(video.title, 'test_video1')
        # check that the websites and books tabs display a message saying
        # nothing had been found and contexts are empty
        self.assertContains(
            resp, 'No websites matched your search - "test_video1"'
        )
        self.assertEqual(len(resp.context['websites']), 0)
        self.assertContains(
            resp, 'No books matched your search - "test_video1"'
        )
        self.assertEqual(len(resp.context['books']), 0)

    def test_search_bar_filters_by_subcategory(self):
        resp = self.client.get(
            '/category/python/django/?search_box=test_website6'
        )
        self.assertEqual(resp.status_code, 200)
        # no items should be found
        self.assertContains(
            resp, 'No videos matched your search - "test_website6"'
        )
        self.assertEqual(len(resp.context['videos']), 0)
        self.assertContains(
            resp, 'No websites matched your search - "test_website6"'
        )
        self.assertEqual(len(resp.context['websites']), 0)
        self.assertContains(
            resp, 'No books matched your search - "test_website6"'
        )
        self.assertEqual(len(resp.context['books']), 0)


class CreateWebsiteRecommendationViewTests(TestCase):

    def setUp(self):
        # create test user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test website
        test_website1 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website1',
            description='test description 1',
            url='http://www.test.com'
        )

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/new_website/'
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/create_website.html')

    def test_HTTP404_for_invalid_category_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=('test', test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_invalid_subcategory_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        url = reverse('create_website', args=(test_category1.slug, 'test',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_form_invalid_when_fields_are_empty(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'title', 'This field is required.')
        self.assertFormError(resp, 'form', 'description',
                             'This field is required.')
        self.assertFormError(resp, 'form', 'url', 'This field is required.')

    def test_form_invalid_when_same_website_is_recommended(self):
        # if a user trys to recomend a website which has the same url
        # that already exists for that subcategory, an error should
        # be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'title': 'test', 'description': 'test',
                                      'url': 'www.test.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'url',
                             'This website has already been recommended!')

    def test_redirect_when_form_valid(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'title': 'test2', 'description': 'test2',
                                      'url': 'www.test2.com'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

    def test_get_image_url_is_successful(self):
        # test grabbing the og:image from meta
        # pinterest image can change so if this fails check image link first
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'title': 'pinterest',
                                      'description': 'test',
                                      'url': 'www.pinterest.com'})
        pinterest = WebsiteRecommendation.objects.get(title='pinterest')
        self.assertEqual(pinterest.image_url,
            'https://s.pinimg.com/images/facebook_share_image.png')

    def test_get_image_url_is_unsuccessful(self):
        # if there is no og:image in the meta tags, it should set the url
        # as None.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_website', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'title': 'django',
                                      'description': 'test',
                                      'url': 'www.djangoproject.com'})
        django = WebsiteRecommendation.objects.get(title='django')
        self.assertEqual(django.image_url, None)


class DeleteWebsiteRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test website
        test_website1 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website1',
            description='test description 1',
            url='http://www.test.com'
        )

    def test_redirect_if_not_logged_in(self):
        website = WebsiteRecommendation.objects.get(title='test_website1')
        url = reverse('delete_website', args=(website.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/delete_website/%s/' % website.pk
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website1')
        url = reverse('delete_website', args=(website.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website1')
        url = reverse('delete_website', args=(website.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/delete_website.html')

    def test_HTTP404_for_invalid_website_pk_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website1')
        wrong_pk = website.pk + 1
        url = reverse('delete_website', args=(wrong_pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_user_without_permision(self):
        # If a user who did not create the website recommendation tries to
        # delete someone else's, it should show 404 error
        login = self.client.login(username='testuser2', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website1')
        url = reverse('delete_website', args=(website.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_when_delete_is_successful(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website1')
        url = reverse('delete_website', args=(website.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))


class ProfilePageViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create 5 websites
        today = timezone.now()

        number_of_websites = 5
        for website_num in range(number_of_websites):
            website = WebsiteRecommendation.objects.create(
                website_author=test_user1,
                category=test_category1,
                subcategory=test_subcategory1,
                title='test_website%s' % website_num,
                description='test description %s' % website_num,
                url='www.testurl%s.com' % website_num,
                image_url='www.testimageurl%s.com' % website_num,
                created_date=today - timezone.timedelta(days=website_num)
            )
            # add bookmark
            website.bookmark.add(test_user1)

        # create website bookmarked by different user
        website_1 = WebsiteRecommendation.objects.create(
            website_author=test_user2,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website_bookmark',
            description='test description',
            url='www.testurl76.com',
            image_url='www.testimageurl76.com',
            created_date=today
        )
        # add bookmark
        website_1.bookmark.add(test_user2)

        # create 5 books
        number_of_books = 5
        isbn_list = (1449340377, 1491912057, 1491933178, 1785881116,
                     1491946008)
        count = 0
        for book_num in range(number_of_books):
            book = BookRecommendation.objects.create(
                isbn=isbn_list[count],
                title='test_book%s' % book_num,
                recommended_by=test_user1,
                category=test_category1,
                subcategory=test_subcategory1,
                book_author='test_book_author%s' % book_num,
                book_description='book description',
                book_url='www.testurl%s.com' % book_num,
                book_image_url='www.testimageurl%s.com' % book_num,
                book_publish_date=today,
                created_date=today - timezone.timedelta(days=book_num)
            )
            # add upvotes
            book.bookmark.add(test_user1)
            count += 1

        # create 5 videos
        number_of_videos = 5
        for video_num in range(number_of_videos):
            video = VideoRecommendation.objects.create(
                title='test_video%s' % video_num,
                recommended_by=test_user1,
                category=test_category1,
                subcategory=test_subcategory1,
                video_description = 'video description',
                video_publish_date = today,
                video_url = 'www.testurl%s.com' % video_num,
                video_image_url = 'www.testimageurl%s.com' % video_num,
                video_id = 1234 + video_num,
                created_date=today - timezone.timedelta(days=video_num)
            )
            # add upvotes
            video.bookmark.add(test_user1)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/user/testuser1/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('user_profile', args=('testuser1',)))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('user_profile', args=('testuser1',)))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/profile.html')

    def test_HTTP404_for_invalid_user_in_kwargs(self):
        resp = self.client.get(reverse('user_profile', args=('mrbean',)))
        self.assertEqual(resp.status_code, 404)

    def test_ordering_of_bookmarks(self):
        # Should order by newest date first. There is no ordering by votes.
        resp = self.client.get(reverse('user_profile', args=('testuser1',)))
        self.assertEqual(resp.status_code, 200)
        bookmark_list = resp.context['bookmark_list']
        date = timezone.now()
        for bookmark in bookmark_list:
            self.assertLessEqual(bookmark.created_date, date)
            date = bookmark.created_date

    def test_bookmark_filtering(self):
        # only items bookmarked by the profile user should be displayed
        # check that bookmarks created by other user are not shown.
        resp = self.client.get(reverse('user_profile', args=('testuser2',)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "test_website_bookmark")
        self.assertEqual(len(resp.context['bookmark_list']), 1)

    def test_ordering_of_recommendations(self):
        # Should order by newest date first. There is no ordering by votes.
        resp = self.client.get(reverse('user_profile', args=('testuser1',)))
        self.assertEqual(resp.status_code, 200)
        recommendations_list = resp.context['recommendations_list']
        date = timezone.now()
        for recommendation in recommendations_list:
            self.assertLessEqual(recommendation.created_date, date)
            date = recommendation.created_date

    def test_recommendation_filtering(self):
        # only items recommended by the profile user should be displayed
        # check that recommendations created by other user are not shown.
        resp = self.client.get(reverse('user_profile', args=('testuser2',)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "test_website_bookmark")
        self.assertEqual(len(resp.context['recommendations_list']), 1)


class UpvoteWebsiteViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # website with no upvotes
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('upvote_website'))
        self.assertRedirects(resp, '/accounts/login/?next=/upvote_website/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.post(
            reverse('upvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.get(reverse('upvote_website'))
        self.assertEqual(resp.status_code, 405)

    def test_upvote_website_view_increases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.post(
            reverse('upvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(website.total_votes, 1)

    def test_upvote_website_view_decreases_if_pressed_again(self):
        # if the user has already upvoted before and they press the upvote
        # again, it must remove the previous upvote.
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        test_user1 = User.objects.get(username='testuser1')
        website.upvote.add(test_user1)
        resp = self.client.post(
            reverse('upvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(website.total_votes, 0)


class DownvoteWebsiteViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # website with no upvotes
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('downvote_website'))
        self.assertRedirects(resp, '/accounts/login/?next=/downvote_website/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.post(
            reverse('downvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.get(reverse('downvote_website'))
        self.assertEqual(resp.status_code, 405)

    def test_downvote_website_view_decreases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.post(
            reverse('downvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(website.total_votes, -1)

    def test_downvote_website_view_increases_if_pressed_again(self):
        # if the user has already downvoted before and they press the downvote
        # again, it must remove the previous downvote.
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        test_user1 = User.objects.get(username='testuser1')
        website.downvote.add(test_user1)
        resp = self.client.post(
            reverse('downvote_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(website.total_votes, 0)


class BookmarkWebsiteViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # website which has not been bookmarked
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('bookmark_website'))
        self.assertRedirects(resp, '/accounts/login/?next=/bookmark_website/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.post(
            reverse('bookmark_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        resp = self.client.get(reverse('bookmark_website'))
        self.assertEqual(resp.status_code, 405)

    def test_bookmark_website(self):
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        test_user1 = User.objects.get(username='testuser1')
        resp = self.client.post(
            reverse('bookmark_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(website.bookmark.count(), 1)
        self.assertTrue(website.bookmark.filter(username='testuser1').exists())


    def test_remove_website_bookmark(self):
        # if the user has already bookmarked this website, if the bookmark
        # button is clicked again it should remove the bookmark.
        login = self.client.login(username='testuser1', password='12345')
        website = WebsiteRecommendation.objects.get(title='test_website')
        test_user1 = User.objects.get(username='testuser1')
        website.bookmark.add(test_user1)
        self.assertEqual(website.bookmark.count(), 1)
        resp = self.client.post(
            reverse('bookmark_website'),
            {'websiteid': website.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(website.bookmark.count(), 0)

class WebsiteCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        today = timezone.now()
        # create website
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=today
        )
        # create 5 comments
        number_of_comments = 5
        for comment_num in range(number_of_comments):
            WebsiteComment.objects.create(
                website=website,
                author=test_user1,
                text='Comment %s' % comment_num,
                created_date=today - timezone.timedelta(days=comment_num)
            )

    def test_view_url_accessible_by_name(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/website_comment.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=('test',
                                               test_subcategory1.slug,
                                               website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                               'test',
                                               website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                               test_subcategory1.slug,
                                               (website.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_comments_are_ordered_by_newest_first(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        comments = resp.context['comments']
        date = timezone.now()
        for comment in comments:
            self.assertLessEqual(comment.created_date, date)
            date = comment.created_date

    def test_redirects_to_website_comments_on_success(self):
        # should redirect back to the same page after successfully posting
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertRedirects(resp, url)

    def test_post_website_comment_if_not_logged_in(self):
        # should not allow comments if not logged in - will reload page if
        # it is tried.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/website_comment.html')

    def test_comment_saves_correctly(self):
        # test the correct information is saved
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('website_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           website.pk))
        resp = self.client.post(url, {'text': 'test comment uploaded'})
        self.assertRedirects(resp, url)
        comment = WebsiteComment.objects.get(text='test comment uploaded')
        self.assertEqual(comment.author,
                         User.objects.get(username='testuser1'))
        self.assertEqual(comment.website, website)


class EditWebsiteCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create website
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

        # create comment
        comment = WebsiteComment.objects.create(
            website=website,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/edit_website_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/edit_website_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_website_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('edit_website_comment', args=(comment.pk,))
        resp = self.client.post(url, {'text': 'test comment edited'})
        redirect_url = reverse('website_comment', args=(comment.website.category.slug,
                                           comment.website.subcategory.slug,
                                           comment.website.pk))
        self.assertRedirects(resp, redirect_url)

class DeleteWebsiteCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create website
        website = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='www.testurl.com',
            image_url='www.testimageurl.com',
            created_date=timezone.now()
        )

        # create comment
        comment = WebsiteComment.objects.create(
            website=website,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/delete_website_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/delete_website_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_website_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = WebsiteComment.objects.get(text='Test comment')
        url = reverse('delete_website_comment', args=(comment.pk,))
        resp = self.client.post(url, {})
        redirect_url = reverse('website_comment', args=(comment.website.category.slug,
                                           comment.website.subcategory.slug,
                                           comment.website.pk))
        self.assertRedirects(resp, redirect_url)


class CreateBookRecommendationViewTests(TransactionTestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test book to test duplicate error against
        test_book1 = BookRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/new_book/'
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/create_book.html')

    def test_HTTP404_for_invalid_category_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=('test', test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_invalid_subcategory_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        url = reverse('create_book', args=(test_category1.slug, 'test',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_when_form_valid(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': 1593275994})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

    def test_form_invalid_when_same_book_is_recommended(self):
        # if a user trys to recomend a book which has the same isbn
        # that already exists for that subcategory, an error should
        # be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': 1593276036})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
                             'This book has already been recommended!')

    def test_form_invalid_when_isbn_too_short(self):
        # if a user trys to input an isbn which is too short an error
        # should be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': 159327603})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
            'Invalid ISBN: Wrong length',
            'Ensure this value has at least 10 characters (it has 9).')

    def test_form_invalid_when_isbn_too_long(self):
        # if a user trys to input an isbn which is too long an error
        # should be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': 15932760367})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
                             'Invalid ISBN: Wrong length')


    def test_form_invalid_when_isbn_is_wrong(self):
        # if a user trys to input an isbn which is wrong an error
        # should be displayed. It is wrong if it is the correct lenght
        # but the numbers fail the checksum.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': 1234567889})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
                             'Invalid ISBN: Failed checksum')

    def test_form_invalid_when_isbn_is_hyphonated(self):
        # if a user trys to input an isbn which has hyphons an error
        # should be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': '99921-58-10-7'})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
                             'Invalid ISBN: Only numbers are allowed')

    def test_problematic_amazon_listing(self):
        # test amazon book which only gives the publication
        # year and not the full date. The view should assign the missing day
        # and month to 1st January to allow it to save.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': '1408884534'})
        self.assertEqual(resp.status_code, 302)
        book = BookRecommendation.objects.get(title='Kid Normal: Tom Fletcher '
                                              'Book Club 2017 title')
        self.assertEqual(book.book_publish_date, date(2017, 1, 1))

    def test_successful_retrieval_of_book_info_from_amazon(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_book', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url, {'isbn': '1593275994'})
        self.assertEqual(resp.status_code, 302)
        book = BookRecommendation.objects.get(title='Automate the Boring '
            'Stuff with Python: Practical Programming for Total Beginners')
        self.assertEqual(book.book_author, 'Al Sweigart')
        self.assertTrue(
            "If you’ve ever spent hours renaming" in book.book_description
        )
        self.assertTrue(
            "www.amazon.com/Automate-Boring-Stuff-Python-Programming" in
            book.book_url
        )
        self.assertEqual(book.book_image_url,
            'https://images-na.ssl-images-amazon.com/images/I/517XL4pO6jL.jpg')
        self.assertEqual(book.book_publish_date, date(2015, 4, 14))

class DeleteBookRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test book
        test_book1 = BookRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('delete_book', args=(book.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/delete_book/%s/' % book.pk
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('delete_book', args=(book.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('delete_book', args=(book.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/delete_book.html')

    def test_HTTP404_for_invalid_book_pk_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        wrong_pk = book.pk + 1
        url = reverse('delete_book', args=(wrong_pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_user_without_permision(self):
        # If a user who did not create the book recommendation tries to
        # delete someone else's, it should show 404 error
        login = self.client.login(username='testuser2', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('delete_book', args=(book.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_when_delete_is_successful(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('delete_book', args=(book.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

class UpvoteBookViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # book with no upvotes
        test_book1 = BookRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('upvote_book'))
        self.assertRedirects(resp, '/accounts/login/?next=/upvote_book/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('upvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('upvote_book'))
        self.assertEqual(resp.status_code, 405)

    def test_upvote_book_view_increases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('upvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(book.total_votes, 1)

    def test_upvote_book_view_decreases_if_pressed_again(self):
        # if the user has already upvoted before and they press the upvote
        # again, it must remove the previous upvote.
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        book.upvote.add(test_user1)
        resp = self.client.post(
            reverse('upvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(book.total_votes, 0)

class DownvoteBookViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # book with no upvotes
        test_book1 = BookRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('downvote_book'))
        self.assertRedirects(resp, '/accounts/login/?next=/downvote_book/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('downvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('downvote_book'))
        self.assertEqual(resp.status_code, 405)

    def test_downvote_book_view_decreases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('downvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(book.total_votes, -1)

    def test_downvote_book_view_increases_if_pressed_again(self):
        # if the user has already downvoted before and they press the downvote
        # again, it must remove the previous downvote.
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        book.downvote.add(test_user1)
        resp = self.client.post(
            reverse('downvote_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(book.total_votes, 0)

class BookmarkBookViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # Book which has not been bookmarked
        test_book1 = BookRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('bookmark_book'))
        self.assertRedirects(resp, '/accounts/login/?next=/bookmark_book/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('bookmark_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('bookmark_book'))
        self.assertEqual(resp.status_code, 405)

    def test_bookmark_book(self):
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        resp = self.client.post(
            reverse('bookmark_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(book.bookmark.count(), 1)
        self.assertTrue(book.bookmark.filter(username='testuser1').exists())


    def test_remove_book_bookmark(self):
        # if the user has already bookmarked this book, if the bookmark
        # button is clicked again it should remove the bookmark.
        login = self.client.login(username='testuser1', password='12345')
        book = BookRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        book.bookmark.add(test_user1)
        self.assertEqual(book.bookmark.count(), 1)
        resp = self.client.post(
            reverse('bookmark_book'),
            {'bookid': book.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(book.bookmark.count(), 0)

class BookCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        today = timezone.now()
        # create book
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
        # create 5 comments
        number_of_comments = 5
        for comment_num in range(number_of_comments):
            BookComment.objects.create(
                book=book,
                author=test_user1,
                text='Comment %s' % comment_num,
                created_date=today - timezone.timedelta(days=comment_num)
            )

    def test_view_url_accessible_by_name(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/book_comment.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=('test',
                                               test_subcategory1.slug,
                                               book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                               'test',
                                               book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                               test_subcategory1.slug,
                                               (book.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_comments_are_ordered_by_newest_first(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        comments = resp.context['comments']
        date = timezone.now()
        for comment in comments:
            self.assertLessEqual(comment.created_date, date)
            date = comment.created_date

    def test_redirects_to_book_comments_on_success(self):
        # should redirect back to the same page after successfully posting
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertRedirects(resp, url)

    def test_post_book_comment_if_not_logged_in(self):
        # should not allow comments if not logged in - will reload page if
        # it is tried.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/book_comment.html')

    def test_comment_saves_correctly(self):
        # test the correct information is saved
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('book_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           book.pk))
        resp = self.client.post(url, {'text': 'test comment uploaded'})
        self.assertRedirects(resp, url)
        comment = BookComment.objects.get(text='test comment uploaded')
        self.assertEqual(comment.author,
                         User.objects.get(username='testuser1'))
        self.assertEqual(comment.book, book)

class EditBookCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create book
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

        # create comment
        comment = BookComment.objects.create(
            book=book,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/edit_book_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/edit_book_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_book_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('edit_book_comment', args=(comment.pk,))
        resp = self.client.post(url, {'text': 'test comment edited'})
        redirect_url = reverse('book_comment',
                               args=(comment.book.category.slug,
                                     comment.book.subcategory.slug,
                                     comment.book.pk))
        self.assertRedirects(resp, redirect_url)

class DeleteBookCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create book
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

        # create comment
        comment = BookComment.objects.create(
            book=book,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/delete_book_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/delete_book_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_book_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = BookComment.objects.get(text='Test comment')
        url = reverse('delete_book_comment', args=(comment.pk,))
        resp = self.client.post(url, {})
        redirect_url = reverse('book_comment', args=(comment.book.category.slug,
                                           comment.book.subcategory.slug,
                                           comment.book.pk))
        self.assertRedirects(resp, redirect_url)

class CreateVideoRecommendationViewTests(TransactionTestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test video to test duplicate error against
        test_video1 = VideoRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                            test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/new_video/'
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                            test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/create_video.html')

    def test_HTTP404_for_invalid_category_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=('test', test_subcategory1.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_invalid_subcategory_name_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        url = reverse('create_video', args=(test_category1.slug, 'test',))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_when_form_valid(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://www.youtube.com/watch?v=V-_O7nl0Ii0'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

    def test_form_invalid_when_same_video_is_recommended(self):
        # if a user trys to recomend a video which has the same youtube id
        # that already exists for that subcategory, an error should
        # be displayed
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'video_url',
                             'This video has already been recommended!')

    def test_youtube_url_with_wrong_video_id(self):
        # test youtube url with an incorrect cideo id
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ34567'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "The Video does not seem to exist! Please "
            "check the URL and try again.")

    def test_small_sized_youtube_url(self):
        # test the smaller youtu.be urls work
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://youtu.be/_OBlgSz8sSM'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

    def test_non_youtube_url(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://vimeo.com/249579173'})
        self.assertFormError(resp, 'form', 'video_url',
            'Please make sure the video you are recommending is from YouTube!')

    def test_youtube_embed_link_valid(self):
        # ensure youtube video embed links work
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://www.youtube.com/embed/_OBlgSz8sSM'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

    def test_successful_retrieval_of_video_info_from_youtube(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        url = reverse('create_video', args=(test_category1.slug,
                                              test_subcategory1.slug))
        resp = self.client.post(url,
            {'video_url': 'https://youtu.be/_OBlgSz8sSM'})
        self.assertEqual(resp.status_code, 302)
        video = VideoRecommendation.objects.get(title='Charlie bit my finger'
            ' - again !')
        self.assertTrue(
            "Charlie bit my finger - again !" in video.video_description
        )
        self.assertEqual(video.video_id, '_OBlgSz8sSM')
        self.assertEqual(video.video_url, 'https://youtu.be/_OBlgSz8sSM')
        self.assertEqual(video.video_image_url,
            'https://i.ytimg.com/vi/_OBlgSz8sSM/hqdefault.jpg')

        # test publish date
class DeleteVideoRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test video
        test_video1 = VideoRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('delete_video', args=(video.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/delete_video/%s/' % video.pk
        )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('delete_video', args=(video.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('delete_video', args=(video.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # check its using the correct template
        self.assertTemplateUsed(resp, 'website/delete_video.html')

    def test_HTTP404_for_invalid_video_pk_in_kwargs(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        wrong_pk = video.pk + 1
        url = reverse('delete_video', args=(wrong_pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_HTTP404_for_user_without_permision(self):
        # If a user who did not create the video recommendation tries to
        # delete someone else's, it should show 404 error
        login = self.client.login(username='testuser2', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('delete_video', args=(video.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_when_delete_is_successful(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('delete_video', args=(video.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

class UpvoteVideoViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # video with no upvotes
        test_video1 = VideoRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('upvote_video'))
        self.assertRedirects(resp, '/accounts/login/?next=/upvote_video/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('upvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('upvote_video'))
        self.assertEqual(resp.status_code, 405)

    def test_upvote_video_view_increases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('upvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(video.total_votes, 1)

    def test_upvote_video_view_decreases_if_pressed_again(self):
        # if the user has already upvoted before and they press the upvote
        # again, it must remove the previous upvote.
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        video.upvote.add(test_user1)
        resp = self.client.post(
            reverse('upvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(video.total_votes, 0)

class DownvoteVideoViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # video with no upvotes
        test_video1 = VideoRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('downvote_video'))
        self.assertRedirects(resp, '/accounts/login/?next=/downvote_video/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('downvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('downvote_video'))
        self.assertEqual(resp.status_code, 405)

    def test_downvote_video_view_decreases_upvote_total_by_1(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('downvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(video.total_votes, -1)

    def test_downvote_video_view_increases_if_pressed_again(self):
        # if the user has already downvoted before and they press the downvote
        # again, it must remove the previous downvote.
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        video.downvote.add(test_user1)
        resp = self.client.post(
            reverse('downvote_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(video.total_votes, 0)

class BookmarkVideoViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # Book which has not been bookmarked
        test_video1 = VideoRecommendation.objects.create(
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

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('bookmark_video'))
        self.assertRedirects(resp, '/accounts/login/?next=/bookmark_video/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.post(
            reverse('bookmark_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)

    def test_405_if_get_request_attempted(self):
        # this tests the @require_POST decorator
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        resp = self.client.get(reverse('bookmark_video'))
        self.assertEqual(resp.status_code, 405)

    def test_bookmark_video(self):
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        resp = self.client.post(
            reverse('bookmark_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(video.bookmark.count(), 1)
        self.assertTrue(video.bookmark.filter(username='testuser1').exists())


    def test_remove_book_bookmark(self):
        # if the user has already bookmarked this video, if the bookmark
        # button is clicked again it should remove the bookmark.
        login = self.client.login(username='testuser1', password='12345')
        video = VideoRecommendation.objects.get(title='test title')
        test_user1 = User.objects.get(username='testuser1')
        video.bookmark.add(test_user1)
        self.assertEqual(video.bookmark.count(), 1)
        resp = self.client.post(
            reverse('bookmark_video'),
            {'videoid': video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(video.bookmark.count(), 0)

class VideoCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        today = timezone.now()
        # create website
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
        # create 5 comments
        number_of_comments = 5
        for comment_num in range(number_of_comments):
            VideoComment.objects.create(
                video=video,
                author=test_user1,
                text='Comment %s' % comment_num,
                created_date=today - timezone.timedelta(days=comment_num)
            )

    def test_view_url_accessible_by_name(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/video_comment.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=('test',
                                               test_subcategory1.slug,
                                               video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                               'test',
                                               video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                               test_subcategory1.slug,
                                               (video.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_comments_are_ordered_by_newest_first(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        comments = resp.context['comments']
        date = timezone.now()
        for comment in comments:
            self.assertLessEqual(comment.created_date, date)
            date = comment.created_date

    def test_redirects_to_video_comments_on_success(self):
        # should redirect back to the same page after successfully posting
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertRedirects(resp, url)

    def test_post_video_comment_if_not_logged_in(self):
        # should not allow comments if not logged in - will reload page if
        # it is tried.
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.post(url, {'text': 'test comment'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/video_comment.html')

    def test_comment_saves_correctly(self):
        # test the correct information is saved
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('video_comment', args=(test_category1.slug,
                                           test_subcategory1.slug,
                                           video.pk))
        resp = self.client.post(url, {'text': 'test comment uploaded'})
        self.assertRedirects(resp, url)
        comment = VideoComment.objects.get(text='test comment uploaded')
        self.assertEqual(comment.author,
                         User.objects.get(username='testuser1'))
        self.assertEqual(comment.video, video)

class EditVideoCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create video
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

        # create comment
        comment = VideoComment.objects.create(
            video=video,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/edit_video_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/edit_video_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_video_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('edit_video_comment', args=(comment.pk,))
        resp = self.client.post(url, {'text': 'test comment edited'})
        redirect_url = reverse('video_comment',
                               args=(comment.video.category.slug,
                                     comment.video.subcategory.slug,
                                     comment.video.pk))
        self.assertRedirects(resp, redirect_url)

class DeleteVideoCommentViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create video
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

        # create comment
        comment = VideoComment.objects.create(
            video=video,
            author=test_user1,
            text='Test comment',
            created_date=timezone.now()
            )

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'website/delete_video_comment.html')

    def test_404_for_comment_pk_that_does_not_exist(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk + 1,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/delete_video_comment/%s/' % comment.pk
        )

    def test_404_if_not_comment_author(self):
        # if another user who is not the author of the comment tries to edit
        # the comment, a 404 shoud be shown.
        login = self.client.login(username='testuser2', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_redirects_to_video_comments_on_success(self):
        login = self.client.login(username='testuser1', password='12345')
        comment = VideoComment.objects.get(text='Test comment')
        url = reverse('delete_video_comment', args=(comment.pk,))
        resp = self.client.post(url, {})
        redirect_url = reverse('video_comment', args=(comment.video.category.slug,
                                           comment.video.subcategory.slug,
                                           comment.video.pk))
        self.assertRedirects(resp, redirect_url)

class ReportWebsiteRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test website
        test_website1 = WebsiteRecommendation.objects.create(
            website_author=test_user1,
            category=test_category1,
            subcategory=test_subcategory1,
            title='test_website',
            description='test description',
            url='http://www.test.com'
        )

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation',
            args=(test_category1.slug, test_subcategory1.slug, website.pk))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/%s/'
                  'report_website_recommendation/' % website.pk
        )

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
            'website/report_website_recommendation.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=('test',
            test_subcategory1.slug, website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=(
            test_category1.slug, 'test', website.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=(
        test_category1.slug, test_subcategory1.slug, (website.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_report_website_email(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, website.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            'Noobhub recommendation report!')

    def test_redirect_after_report_email_is_sent(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        website = WebsiteRecommendation.objects.get(title='test_website')
        url = reverse('report_website_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, website.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))


class ReportBookRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test book
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

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation',
            args=(test_category1.slug, test_subcategory1.slug, book.pk))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/%s/'
                  'report_book_recommendation/' % book.pk
        )

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
            'website/report_book_recommendation.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=('test',
            test_subcategory1.slug, book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=(
            test_category1.slug, 'test', book.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=(
        test_category1.slug, test_subcategory1.slug, (book.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_report_book_email(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, book.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            'Noobhub recommendation report!')

    def test_redirect_after_report_email_is_sent(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        book = BookRecommendation.objects.get(title='test title')
        url = reverse('report_book_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, book.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))

class ReportVideoRecommendationViewTests(TestCase):

    def setUp(self):
        # create test users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='12345')
        test_user1.save()
        # create test category
        test_category1 = Category.objects.create(name='python')
        test_category1.save()
        # create test subcategory with same category
        test_subcategory1 = SubCategory.objects.create(name='django',
                                                       category=test_category1)
        # create test video
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

    def test_redirect_if_not_logged_in(self):
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation',
            args=(test_category1.slug, test_subcategory1.slug, video.pk))
        resp = self.client.get(url)
        self.assertRedirects(
            resp, '/accounts/login/?next=/category/python/django/%s/'
                  'report_video_recommendation/' % video.pk
        )

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
            'website/report_video_recommendation.html')

    def test_url_with_category_that_does_not_exist(self):
        # if a category is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=('test',
            test_subcategory1.slug, video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def test_url_with_subcategory_that_does_not_exist(self):
        # if a subcategory is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=(
            test_category1.slug, 'test', video.pk))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url_with_pk_that_does_not_exist(self):
        # if a pk is manually typed into the url a 404 should be
        # shown if it does not exist.
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=(
        test_category1.slug, test_subcategory1.slug, (video.pk + 1)))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_report_book_email(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, video.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            'Noobhub recommendation report!')

    def test_redirect_after_report_email_is_sent(self):
        login = self.client.login(username='testuser1', password='12345')
        test_category1 = Category.objects.get(name='python')
        test_subcategory1 = SubCategory.objects.get(name='django')
        video = VideoRecommendation.objects.get(title='test title')
        url = reverse('report_video_recommendation', args=(
            test_category1.slug, test_subcategory1.slug, video.pk))
        resp = self.client.get(url, {'message_box': 'test report message'})
        self.assertRedirects(resp, reverse('subcategory',
                                           args=(test_category1.slug,
                                                 test_subcategory1.slug,)))
