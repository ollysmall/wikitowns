from django.shortcuts import render
from django.http import HttpResponse, Http404
from website.models import (Category, SubCategory, WebsiteRecommendation,
                            WebsiteComment, BookRecommendation, BookComment,
                            VideoRecommendation, VideoComment)
from website.forms import (WebsiteForm, WebsiteCommentForm, BookForm,
                           BookCommentForm, VideoForm, VideoCommentForm,
                           DateFilterForm, SearchForm, ReportForm)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from datetime import date, datetime
from itertools import chain
from operator import attrgetter
from django.contrib.postgres.search import (SearchQuery, SearchRank,
                                            SearchVector)
from django.core.mail import send_mail
from urllib.request import urlopen, Request
# for amazon book info
import os
import bottlenose
from bs4 import BeautifulSoup
# for youtube api
from apiclient.discovery import build
from apiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
# for unlimted scroll pagination
from el_pagination.decorators import page_templates, page_template


def index(request):
    category_img = Category.category_img
    context_dict = {'category_img': category_img}
    return render(request, 'website/index.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        subcategory = (SubCategory.objects
                                  .filter(category=category)
                                  .order_by('name'))
        context_dict['subcategories'] = subcategory
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    return render(request, 'website/category.html', context_dict)


@page_templates({
    'website/subcategory_website_page.html': None,
    'website/subcategory_book_page.html': 'other_entries_page',
    'website/subcategory_video_page.html': 'other_entries_page2',
})
def subcategory(request, category_name_slug, subcategory_name_slug,
                template='website/subcategory.html', extra_context=None):
    context_dict = {}
    # set the initial using what was sent in the get request
    form = DateFilterForm(initial=request.GET)
    context_dict['form'] = form
    search_form = SearchForm(initial=request.GET)
    context_dict['search_form'] = search_form
    # get todays date for filtering recommendations by
    today = date.today()

    try:
        user = request.user
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category'] = category
        subcategory = SubCategory.objects.get(slug=subcategory_name_slug,
                                              category=category)
        context_dict['subcategory_name'] = subcategory.name
        context_dict['subcategory'] = subcategory
        website_list = (
            WebsiteRecommendation
            .objects
            .filter(subcategory=subcategory)
            .annotate(totalvotes=Count('upvote') - Count('downvote'))
            .order_by('-totalvotes')
        )
        context_dict['websites'] = website_list
        book_list = (
            BookRecommendation
            .objects
            .filter(subcategory=subcategory)
            .annotate(totalvotes=Count('upvote') - Count('downvote'))
            .order_by('-totalvotes')
        )
        context_dict['books'] = book_list
        video_list = (
            VideoRecommendation
            .objects
            .filter(subcategory=subcategory)
            .annotate(totalvotes=Count('upvote') - Count('downvote'))
            .order_by('-totalvotes')
        )
        context_dict['videos'] = video_list

    except SubCategory.DoesNotExist:
        pass

    except Category.DoesNotExist:
        pass

    if request.method == 'GET':
        form = DateFilterForm(request.GET)

        if form.is_valid():
            filter_type = (form.cleaned_data['time_filter'])

            if filter_type == 'newest':
                website_list = (
                    WebsiteRecommendation
                    .objects
                    .filter(subcategory=subcategory)
                    .order_by('-created_date')
                )
                context_dict['websites'] = website_list
                book_list = (
                    BookRecommendation
                    .objects
                    .filter(subcategory=subcategory)
                    .order_by('-created_date')
                )
                context_dict['books'] = book_list
                video_list = (
                    VideoRecommendation
                    .objects
                    .filter(subcategory=subcategory)
                    .order_by('-created_date')
                )
                context_dict['videos'] = video_list
            elif filter_type == 'best-of-year':
                website_list = (
                    WebsiteRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['websites'] = website_list
                book_list = (
                    BookRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['books'] = book_list
                video_list = (
                    VideoRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['videos'] = video_list
            elif filter_type == 'best-of-month':
                website_list = (
                    WebsiteRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year,
                            created_date__month=today.month)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['websites'] = website_list
                book_list = (
                    BookRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year,
                            created_date__month=today.month)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['books'] = book_list
                video_list = (
                    VideoRecommendation
                    .objects
                    .filter(subcategory=subcategory,
                            created_date__year=today.year,
                            created_date__month=today.month)
                    .annotate(totalvotes=Count('upvote') - Count('downvote'))
                    .order_by('-totalvotes')
                )
                context_dict['videos'] = video_list

        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            search_keywords = (search_form.cleaned_data['search_box'])
            context_dict['search_keywords'] = search_keywords

            if search_keywords != '':
                # add weighting to gear more towards title?
                website_list = (
                    WebsiteRecommendation
                    .objects
                    .annotate(search=SearchVector('title', 'description'),)
                    .filter(subcategory=subcategory,
                            search=SearchQuery(search_keywords))
                )
                context_dict['websites'] = website_list
                book_list = (
                    BookRecommendation
                    .objects
                    .annotate(search=SearchVector('title',
                                                  'book_description'),)
                    .filter(subcategory=subcategory,
                            search=SearchQuery(search_keywords))
                )
                context_dict['books'] = book_list
                video_list = (
                    VideoRecommendation
                    .objects
                    .annotate(search=SearchVector('title',
                                                  'video_description'),)
                    .filter(subcategory=subcategory,
                            search=SearchQuery(search_keywords))
                )
                context_dict['videos'] = video_list

    if extra_context is not None:
        context_dict.update(extra_context)
    return render(request, template, context_dict)


class CreateWebsiteRecommendation(CreateView):
    model = WebsiteRecommendation
    form_class = WebsiteForm
    template_name = 'website/create_website.html'

    def get_form_kwargs(self):
        kwargs = super(CreateWebsiteRecommendation, self).get_form_kwargs()
        kwargs['category'] = (
            get_object_or_404(Category, slug=self.kwargs["category_name_slug"])
        )
        kwargs['subcategory'] = (
            get_object_or_404(SubCategory,
                              slug=self.kwargs["subcategory_name_slug"],
                              category=kwargs['category']
                              )
        )
        return kwargs

    def form_valid(self, form):
        website_url = (form.cleaned_data['url'])
        form.instance.url = website_url.lower()
        form.instance.category = (
            Category
            .objects
            .get(slug=self.kwargs["category_name_slug"])
        )
        form.instance.subcategory = (
            SubCategory
            .objects
            .get(slug=self.kwargs["subcategory_name_slug"])
        )
        form.instance.website_author = self.request.user

        try:
            # headers used as some websites dont let you use urlopen on them
            webpage = urlopen(Request(
                website_url, headers={'User-Agent': 'Mozilla'})).read()
            soup = BeautifulSoup(webpage, "lxml")
            og_image_url = soup.find("meta", property="og:image", content=True)
            image_url = og_image_url["content"]
            try:
                check_if_url_works = urlopen(Request(
                    image_url, headers={'User-Agent': 'Mozilla'})).read()
                form.instance.image_url = image_url
            except:
                form.instance.image_url = None
        except:
            form.instance.image_url = None
        return super(CreateWebsiteRecommendation, self).form_valid(form)

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug})


class DeleteWebsiteRecommendation(DeleteView):
    model = WebsiteRecommendation
    template_name = 'website/delete_website.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(WebsiteRecommendation, pk=self.kwargs['pk'])
        if obj.website_author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug})


@page_templates({
    'website/profile_bookmarks_page.html': None,
    'website/profile_recommendations_page.html': 'other_entries_page',
})
def profile_page(request, username, template='website/profile.html',
                 extra_context=None):
    context_dict = {}
    user = get_object_or_404(User, username=username)
    context_dict['profile_user'] = user
    website_recommendations = (WebsiteRecommendation
                               .objects
                               .filter(website_author=user))
    book_recommendations = (BookRecommendation
                            .objects.filter(recommended_by=user))
    video_recommendations = (VideoRecommendation
                             .objects
                             .filter(recommended_by=user))

    recommendations_list = sorted(chain(website_recommendations,
                                        book_recommendations,
                                        video_recommendations),
                                  key=attrgetter('created_date'),
                                  reverse=True)
    context_dict['recommendations_list'] = recommendations_list
    website_bookmarks = WebsiteRecommendation.objects.filter(bookmark=user)
    book_bookmarks = BookRecommendation.objects.filter(bookmark=user)
    video_bookmarks = VideoRecommendation.objects.filter(bookmark=user)
    bookmark_list = sorted(chain(website_bookmarks,
                                 book_bookmarks,
                                 video_bookmarks),
                           key=attrgetter('created_date'),
                           reverse=True)
    context_dict['bookmark_list'] = bookmark_list
    if extra_context is not None:
        context_dict.update(extra_context)
    return render(request, template, context_dict)


@login_required
@require_POST
def upvote_website(request):
    if request.method == 'POST':
        user = request.user
        websiteid = request.POST.get('websiteid')
        website = WebsiteRecommendation.objects.get(id=int(websiteid))
        if website.upvote.filter(id=user.id).exists():
            website.upvote.remove(user)
        else:
            website.upvote.add(user)
            if website.downvote.filter(id=user.id).exists():
                website.downvote.remove(user)
    ctx = {'total_website_votes': website.total_votes, }
    return HttpResponse(website.total_votes)


@login_required
@require_POST
def downvote_website(request):
    if request.method == 'POST':
        user = request.user
        websiteid = request.POST.get('websiteid')
        website = WebsiteRecommendation.objects.get(id=int(websiteid))
        if website.downvote.filter(id=user.id).exists():
            website.downvote.remove(user)
        else:
            website.downvote.add(user)
            if website.upvote.filter(id=user.id).exists():
                website.upvote.remove(user)
    ctx = {'total_website_votes': website.total_votes}
    return HttpResponse(website.total_votes)


@login_required
@require_POST
def bookmark_website(request):
    if request.method == 'POST':
        user = request.user
        websiteid = request.POST.get('websiteid')
        website = WebsiteRecommendation.objects.get(id=int(websiteid))
        if website.bookmark.filter(id=user.id).exists():
            website.bookmark.remove(user)
        else:
            website.bookmark.add(user)
    # status 204 = The server successfully processed the request and is not
    # returning any content
    return HttpResponse(status=204)


@page_template('website/website_comment_page.html')
def website_comment(request, category_name_slug, subcategory_name_slug, pk,
                    template='website/website_comment.html',
                    extra_context=None):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    website = get_object_or_404(WebsiteRecommendation, id=pk)
    context_dict['website'] = website
    comments = (WebsiteComment.objects
                              .filter(website=website)
                              .order_by('-created_date')[:100])
    # change the 100 so you can show unlimited comments
    context_dict['comments'] = comments

    if request.method == "POST" and request.user.is_authenticated:
        form = WebsiteCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.website = website
            comment.author = user
            comment.save()
            return redirect('website_comment',
                            category_name_slug=website.category.slug,
                            subcategory_name_slug=website.subcategory.slug,
                            pk=website.pk)

    form = WebsiteCommentForm()
    context_dict['form'] = form
    if extra_context is not None:
        context_dict.update(extra_context)
    return render(request, template, context_dict)


class EditWebsiteComment(UpdateView):
    model = WebsiteComment
    form_class = WebsiteCommentForm
    template_name = 'website/edit_website_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(WebsiteComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.website.category.slug
        subcategory_slug = self.object.website.subcategory.slug
        pk = self.object.website.pk
        return reverse('website_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


class DeleteWebsiteComment(DeleteView):
    model = WebsiteComment
    template_name = 'website/delete_website_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(WebsiteComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.website.category.slug
        subcategory_slug = self.object.website.subcategory.slug
        pk = self.object.website.pk
        return reverse('website_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


@login_required
def create_book_recommendation(request, category_name_slug,
                               subcategory_name_slug):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    form = BookForm(category=category, subcategory=subcategory)

    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_ASSOCIATE_TAG = os.environ['AWS_ASSOCIATE_TAG']

    amazon = bottlenose.Amazon(
                               AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY,
                               AWS_ASSOCIATE_TAG,
                               Parser=lambda text: BeautifulSoup(text, 'xml')
    )
    if request.method == "POST":
        form = BookForm(request.POST, category=category,
                        subcategory=subcategory)
        if form.is_valid():
            isbn = (form.cleaned_data['isbn'])
            book = form.save(commit=False)

            try:
                results = amazon.ItemLookup(ItemId=isbn, ResponseGroup="Medium",
                                            SearchIndex="Books", IdType="ISBN")

                book.book_publish_date = results.find('PublicationDate').string
                # review line below - dont think it is a good way of doing it
                book.book_image_url = results.find('LargeImage').text[:-6]
                book.recommended_by = user
                book.category = category
                book.subcategory = subcategory
                book.title = results.find('Title').string
                book.book_author = results.find('Author').string
                book.book_description = results.find('Content').string
                book.book_url = results.find('DetailPageURL').string
                book.save()
                return redirect('subcategory', category_name_slug=category.slug,
                                subcategory_name_slug=subcategory.slug)
            except:
                messages.error(request, ("Something went wrong, please try "
                                         "again. If this error keeps showing "
                                         "then there may be an issue with "
                                         "the book you are trying to "
                                         "recommend."))

    context_dict['form'] = form
    return render(request, 'website/create_book.html', context_dict)


class DeleteBookRecommendation(DeleteView):
    model = BookRecommendation
    template_name = 'website/delete_book.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(BookRecommendation, pk=self.kwargs['pk'])
        if obj.recommended_by != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug})


@login_required
@require_POST
def upvote_book(request):
    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.upvote.filter(id=user.id).exists():
            book.upvote.remove(user)
        else:
            book.upvote.add(user)
            if book.downvote.filter(id=user.id).exists():
                book.downvote.remove(user)
    ctx = {'total_book_votes': book.total_votes, }
    return HttpResponse(book.total_votes)


@login_required
@require_POST
def downvote_book(request):
    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.downvote.filter(id=user.id).exists():
            book.downvote.remove(user)
        else:
            book.downvote.add(user)
            if book.upvote.filter(id=user.id).exists():
                book.upvote.remove(user)
    ctx = {'total_book_votes': book.total_votes}
    return HttpResponse(book.total_votes)


@login_required
@require_POST
def bookmark_book(request):
    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.bookmark.filter(id=user.id).exists():
            book.bookmark.remove(user)
        else:
            book.bookmark.add(user)
    # status 204 = The server successfully processed the request and is not
    # returning any content
    return HttpResponse(status=204)


@page_template('website/book_comment_page.html')
def book_comment(request, category_name_slug, subcategory_name_slug, pk,
                 template='website/book_comment.html', extra_context=None):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    book = get_object_or_404(BookRecommendation, id=pk)
    context_dict['book'] = book
    comments = (BookComment.objects
                           .filter(book=book)
                           .order_by('-created_date')[:100])
    # change the 100 so you can show unlimited comments
    context_dict['comments'] = comments

    if request.method == "POST" and request.user.is_authenticated:
        form = BookCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.author = user
            comment.save()
            return redirect('book_comment',
                            category_name_slug=book.category.slug,
                            subcategory_name_slug=book.subcategory.slug,
                            pk=book.pk)

            # need an else here incase form is not valid

    form = BookCommentForm()
    context_dict['form'] = form
    if extra_context is not None:
        context_dict.update(extra_context)
    return render(request, template, context_dict)


class EditBookComment(UpdateView):
    model = BookComment
    form_class = BookCommentForm
    template_name = 'website/edit_book_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(BookComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.book.category.slug
        subcategory_slug = self.object.book.subcategory.slug
        pk = self.object.book.pk
        return reverse('book_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


class DeleteBookComment(DeleteView):
    model = BookComment
    template_name = 'website/delete_book_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(BookComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.book.category.slug
        subcategory_slug = self.object.book.subcategory.slug
        pk = self.object.book.pk
        return reverse('book_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


@login_required
def create_video_recommendation(request, category_name_slug,
                                subcategory_name_slug):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    form = VideoForm(category=category, subcategory=subcategory)

    if request.method == "POST":
        # pass the category and subcategory to the form to enable validation
        # on duplicates
        form = VideoForm(request.POST, category=category,
                         subcategory=subcategory)
        if form.is_valid():
            try:
                url = (form.cleaned_data['video_url'])
                video = form.save(commit=False)
                if url.startswith(('youtu', 'www')):
                    url = 'http://' + url
                query = urlparse(url)
                if 'youtube' in query.hostname:
                    if query.path == '/watch':
                        video_id = parse_qs(query.query)['v'][0]
                    elif query.path.startswith(('/embed/', '/v/')):
                        video_id = query.path.split('/')[2]
                elif 'youtu.be' in query.hostname:
                    video_id = query.path[1:]
                else:
                    raise ValueError

                DEVELOPER_KEY = os.environ['YOUTUBE_DEVELOPER_KEY']
                YOUTUBE_API_SERVICE_NAME = "youtube"
                YOUTUBE_API_VERSION = "v3"

                youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                developerKey=DEVELOPER_KEY)

                search_response = youtube.videos().list(
                  id=video_id,
                  part='snippet'
                ).execute()

                # check that a video has been found by seing if the results
                # returned is greater than 0
                if search_response["pageInfo"]["totalResults"] > 0:
                    for item in search_response["items"]:
                        title = item["snippet"]["title"]
                        description = item["snippet"]["description"]
                        # some videos do not have the standard thumbnail,
                        # get high quality thumbnail if the standard one
                        # is not available.
                        try:
                            thumbnail = (item["snippet"]["thumbnails"]
                                         ["standard"]["url"])
                        except:
                            thumbnail = (item["snippet"]["thumbnails"]["high"]
                                         ["url"])

                        publish_date = item["snippet"]["publishedAt"]

                    video.category = category
                    video.subcategory = subcategory
                    video.title = title
                    video.recommended_by = user
                    video.video_description = description
                    video.video_publish_date = publish_date
                    video.video_image_url = thumbnail
                    video.video_id = video_id
                    video.save()
                    return redirect('subcategory',
                                    category_name_slug=category.slug,
                                    subcategory_name_slug=subcategory.slug)
                else:
                    messages.error(request, ("The Video does not seem to "
                                             "exist! Please check the URL and "
                                             "try again."))
            except:
                messages.error(request, ("Something went wrong, please check "
                                         "the URL and try again."))

    context_dict['form'] = form
    return render(request, 'website/create_video.html', context_dict)


class DeleteVideoRecommendation(DeleteView):
    model = VideoRecommendation
    template_name = 'website/delete_video.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(VideoRecommendation, pk=self.kwargs['pk'])
        if obj.recommended_by != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug})


@login_required
@require_POST
def upvote_video(request):
    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))
        if video.upvote.filter(id=user.id).exists():
            video.upvote.remove(user)
        else:
            video.upvote.add(user)
            if video.downvote.filter(id=user.id).exists():
                video.downvote.remove(user)

    ctx = {'total_video_votes': video.total_votes, }
    return HttpResponse(video.total_votes)


@login_required
@require_POST
def downvote_video(request):
    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))
        if video.downvote.filter(id=user.id).exists():
            video.downvote.remove(user)
        else:
            video.downvote.add(user)
            if video.upvote.filter(id=user.id).exists():
                video.upvote.remove(user)

    ctx = {'total_video_votes': video.total_votes}
    return HttpResponse(video.total_votes)


@login_required
@require_POST
def bookmark_video(request):
    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))
        if video.bookmark.filter(id=user.id).exists():
            video.bookmark.remove(user)
        else:
            video.bookmark.add(user)
    # status 204 = The server successfully processed the request and is not
    # returning any content
    return HttpResponse(status=204)


@page_template('website/video_comment_page.html')
def video_comment(request, category_name_slug, subcategory_name_slug, pk,
                  template='website/video_comment.html', extra_context=None):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    video = get_object_or_404(VideoRecommendation, id=pk)
    context_dict['video'] = video
    comments = (VideoComment.objects
                            .filter(video=video)
                            .order_by('-created_date'))
    context_dict['comments'] = comments

    if request.method == "POST" and request.user.is_authenticated:
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = video
            comment.author = user
            comment.save()
            return redirect('video_comment',
                            category_name_slug=video.category.slug,
                            subcategory_name_slug=video.subcategory.slug,
                            pk=video.pk)

            # need an else here incase form is not valid

    form = VideoCommentForm()
    context_dict['form'] = form
    if extra_context is not None:
        context_dict.update(extra_context)
    return render(request, template, context_dict)


class EditVideoComment(UpdateView):
    model = VideoComment
    form_class = VideoCommentForm
    template_name = 'website/edit_video_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(VideoComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.video.category.slug
        subcategory_slug = self.object.video.subcategory.slug
        pk = self.object.video.pk
        return reverse('video_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


class DeleteVideoComment(DeleteView):
    model = VideoComment
    template_name = 'website/delete_video_comment.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(VideoComment, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.video.category.slug
        subcategory_slug = self.object.video.subcategory.slug
        pk = self.object.video.pk
        return reverse('video_comment',
                       kwargs={'category_name_slug': category_slug,
                               'subcategory_name_slug': subcategory_slug,
                               'pk': pk})


@login_required
def report_website_recommendation(request, category_name_slug,
                                  subcategory_name_slug, pk):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    website = get_object_or_404(WebsiteRecommendation, id=pk)
    context_dict['website'] = website
    form = ReportForm()
    context_dict['form'] = form

    if request.method == 'GET':
        report_form = ReportForm(request.GET)
        if report_form.is_valid():
            report_message = (report_form.cleaned_data['message_box'])
            email_message = ('Reported by: ' + str(user)
                             + '\nType: Website'
                             + '\nCategory: ' + str(category)
                             + '\nSubcategory: ' + str(subcategory)
                             + '\nRecommended by: '
                             + str(website.website_author)
                             + '\nTitle: ' + str(website.title)
                             + '\nIssue reported: ' + report_message)
            send_mail('Noobhub recommendation report!', email_message,
                      'noobhubio@gmail.com', ['oliver@rotherfields.co.uk'],
                      fail_silently=False,)
            return redirect('subcategory', category_name_slug=category.slug,
                            subcategory_name_slug=subcategory.slug)

    return render(request, 'website/report_website_recommendation.html',
                  context_dict)


@login_required
def report_book_recommendation(request, category_name_slug,
                               subcategory_name_slug, pk):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    book = get_object_or_404(BookRecommendation, id=pk)
    context_dict['book'] = book
    form = ReportForm()
    context_dict['form'] = form

    if request.method == 'GET':
        report_form = ReportForm(request.GET)
        if report_form.is_valid():
            report_message = (report_form.cleaned_data['message_box'])
            email_message = ('Reported by: ' + str(user)
                             + '\nType: Book'
                             + '\nCategory: ' + str(category)
                             + '\nSubcategory: ' + str(subcategory)
                             + '\nRecommended by: ' + str(book.recommended_by)
                             + '\nTitle: ' + str(book.title)
                             + '\nIssue reported: ' + report_message)
            send_mail('Noobhub recommendation report!', email_message,
                      'noobhubio@gmail.com', ['oliver@rotherfields.co.uk'],
                      fail_silently=False,)
            return redirect('subcategory', category_name_slug=category.slug,
                            subcategory_name_slug=subcategory.slug)

    return render(request, 'website/report_book_recommendation.html',
                  context_dict)


@login_required
def report_video_recommendation(request, category_name_slug,
                                subcategory_name_slug, pk):
    context_dict = {}
    user = request.user
    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category
    subcategory = get_object_or_404(SubCategory, slug=subcategory_name_slug,
                                    category=category)
    context_dict['subcategory'] = subcategory
    video = get_object_or_404(VideoRecommendation, id=pk)
    context_dict['video'] = video
    form = ReportForm()
    context_dict['form'] = form

    if request.method == 'GET':
        report_form = ReportForm(request.GET)
        if report_form.is_valid():
            report_message = (report_form.cleaned_data['message_box'])
            email_message = ('Reported by: ' + str(user)
                             + '\nType: Video'
                             + '\nCategory: ' + str(category)
                             + '\nSubcategory: ' + str(subcategory)
                             + '\nRecommended by: ' + str(video.recommended_by)
                             + '\nTitle: ' + str(video.title)
                             + '\nIssue reported: ' + report_message)
            send_mail('Noobhub recommendation report!', email_message,
                      'noobhubio@gmail.com', ['oliver@rotherfields.co.uk'],
                      fail_silently=False,)
            return redirect('subcategory', category_name_slug=category.slug,
                            subcategory_name_slug=subcategory.slug)

    return render(request, 'website/report_video_recommendation.html',
                  context_dict)
