from django.shortcuts import render
from django.http import HttpResponse, Http404
from website.models import Category, SubCategory, WebsiteRecommendation, WebsiteComment, BookRecommendation, BookComment, VideoRecommendation, VideoComment
from website.forms import WebsiteForm, WebsiteCommentForm, BookForm, BookCommentForm, VideoForm, VideoCommentForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt #get rid of this
from django.db.models import Count

#for amazon book info
import os
import bottlenose
from bs4 import BeautifulSoup

#for youtube api
from apiclient.discovery import build
from apiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs

def index(request):
    category_list = Category.objects.order_by('name')
    category_img = Category.category_img
    context_dict = {'categories': category_list, 'category_img': category_img}
    return render(request, 'website/index.html', context_dict)

def category(request, category_name_slug):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        subcategory = SubCategory.objects.filter(category=category).order_by('name')
        context_dict['subcategory'] = subcategory
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    return render(request, 'website/category.html', context_dict)

def subcategory(request, category_name_slug, subcategory_name_slug):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}



    try:
        user = request.user
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category'] = category
        subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
        context_dict['subcategory_name'] = subcategory.name
        context_dict['subcategory'] = subcategory
        website_list = WebsiteRecommendation.objects.filter(subcategory=subcategory).annotate(totalvotes=Count('upvote') - Count('downvote')).order_by('-totalvotes')
        context_dict['websites'] = website_list
        book_list = BookRecommendation.objects.filter(subcategory=subcategory).annotate(totalvotes=Count('upvote') - Count('downvote')).order_by('-totalvotes')
        context_dict['books'] = book_list
        video_list = VideoRecommendation.objects.filter(subcategory=subcategory).annotate(totalvotes=Count('upvote') - Count('downvote')).order_by('-totalvotes')
        context_dict['videos'] = video_list

    except SubCategory.DoesNotExist:
        pass

    return render(request, 'website/subcategory.html', context_dict)

class CreateWebsiteRecommendation(CreateView):
    model = WebsiteRecommendation
    form_class = WebsiteForm
    template_name = 'website/create_website.html'

    def get_context_data(self, **kwargs):
        context = super(CreateWebsiteRecommendation, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def form_valid(self, form):
        form.instance.category = Category.objects.get(slug=self.kwargs["category_name_slug"])
        form.instance.subcategory = SubCategory.objects.get(slug=self.kwargs["subcategory_name_slug"])
        form.instance.website_author = self.request.user

        return super(CreateWebsiteRecommendation, self).form_valid(form)

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug})

class DeleteWebsiteRecommendation(DeleteView):
    model = WebsiteRecommendation
    template_name = 'website/delete_website.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteWebsiteRecommendation, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = WebsiteRecommendation.objects.get(pk=self.kwargs['pk'])
        if obj.website_author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug})

def profile_page(request, username):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}

    user = get_object_or_404(User, username=username)
    context_dict['profile_user'] = user
    website_recommendations = WebsiteRecommendation.objects.filter(website_author=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['website_recommendations'] = website_recommendations
    book_recommendations = BookRecommendation.objects.filter(recommended_by=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['book_recommendations'] = book_recommendations
    video_recommendations = VideoRecommendation.objects.filter(recommended_by=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['video_recommendations'] = video_recommendations
    website_bookmarks = WebsiteRecommendation.objects.filter(bookmark=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['website_bookmarks'] = website_bookmarks
    book_bookmarks = BookRecommendation.objects.filter(bookmark=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['book_bookmarks'] = book_bookmarks
    video_bookmarks = VideoRecommendation.objects.filter(bookmark=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['video_bookmarks'] = video_bookmarks
    return render(request, 'website/profile.html', context_dict)

@login_required
@require_POST #check if this is needed - I think the if statement below makes it redundant
def upvote_website(request):

    if request.method == 'POST':
        user = request.user
        websiteid = request.POST.get('websiteid')
        website = WebsiteRecommendation.objects.get(id=int(websiteid))

        if website.upvote.filter(id=user.id).exists():
            # user has already upvoted this website
            # remove upvote
            website.upvote.remove(user)

        else:
            # add a new upvote for this website
            website.upvote.add(user)
            if website.downvote.filter(id=user.id).exists():
                website.downvote.remove(user)



    ctx = {'total_website_votes': website.total_votes,}
    return HttpResponse(website.total_votes)

@login_required
@require_POST
def downvote_website(request):

    if request.method == 'POST':
        user = request.user
        websiteid = request.POST.get('websiteid')
        website = WebsiteRecommendation.objects.get(id=int(websiteid))

        if website.downvote.filter(id=user.id).exists():
            # user has already downvoted this website
            # remove downvote
            website.downvote.remove(user)

        else:
            # add a new downvote for this website
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
            # user has already bookmarked this website
            # remove bookmark
            website.bookmark.remove(user)

        else:
            # add a new bookmark for this website
            website.bookmark.add(user)

    return HttpResponse(website.total_votes) #this should be changed - it doesnt need to respond with total votes

def website_comment(request, category_name_slug, subcategory_name_slug, pk):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
    user = request.user
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category'] = category
    subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
    context_dict['subcategory'] = subcategory
    website = get_object_or_404(WebsiteRecommendation, id=pk)
    context_dict['website'] = website
    comments = WebsiteComment.objects.filter(website=website).order_by('-created_date')[:100] #change the 100 so you can show unlimited comments
    context_dict['comments'] = comments


    if request.method == "POST" and request.user.is_authenticated:
        form = WebsiteCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.website = website
            comment.author = user
            comment.save()
            return redirect('website_comment', category_name_slug=website.category.slug, subcategory_name_slug=website.subcategory.slug, pk=website.pk)

    else:
        form = WebsiteCommentForm()
        context_dict['form'] = form

        return render(request, 'website/website_comment.html', context_dict)

class EditWebsiteComment(UpdateView):
    model = WebsiteComment
    form_class = WebsiteCommentForm
    template_name = 'website/edit_website_comment.html'

    def get_context_data(self, **kwargs):
        context = super(EditWebsiteComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = WebsiteComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.website.category.slug
        subcategory_slug = self.object.website.subcategory.slug
        pk = self.object.website.pk
        return reverse('website_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})

class DeleteWebsiteComment(DeleteView):
    model = WebsiteComment
    template_name = 'website/delete_website_comment.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteWebsiteComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = WebsiteComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.website.category.slug
        subcategory_slug = self.object.website.subcategory.slug
        pk = self.object.website.pk
        return reverse('website_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})

@login_required
def create_book_recommendation(request, category_name_slug, subcategory_name_slug):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
    user = request.user
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category'] = category
    subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
    context_dict['subcategory'] = subcategory

    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_ASSOCIATE_TAG = os.environ['AWS_ASSOCIATE_TAG']

    amazon = bottlenose.Amazon(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG,
    Parser=lambda text: BeautifulSoup(text, 'xml')
    )

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            isbn = (form.cleaned_data['isbn'])
            book = form.save(commit=False)

            results = amazon.ItemLookup(ItemId=isbn, ResponseGroup="Medium",
                SearchIndex="Books", IdType="ISBN")

            book.book_publish_date = results.find('PublicationDate').string
            book.book_image_url = results.find('LargeImage').text[:-6] # review this - dont think it is a good way of doing it
            book.recommended_by = user
            book.category = category
            book.subcategory = subcategory
            book.title = results.find('Title').string
            book.book_author = results.find('Author').string
            book.book_description = results.find('Content').string
            book.book_url = results.find('DetailPageURL').string
            book.save()
            return redirect('subcategory', category_name_slug=category.slug, subcategory_name_slug=subcategory.slug)
        else:
            #need to add proper handling of errors if they enter the wrong isbn
            # got a service unavailable message whilst requesting amazon info - need fallback for this
            form = BookForm()
            context_dict['form'] = form
            return render(request, 'website/create_book.html', context_dict)


    else:
        form = BookForm()
        context_dict['form'] = form

        return render(request, 'website/create_book.html', context_dict)

class DeleteBookRecommendation(DeleteView):
    model = BookRecommendation
    template_name = 'website/delete_book.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteBookRecommendation, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = BookRecommendation.objects.get(pk=self.kwargs['pk'])
        if obj.recommended_by != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug})

@login_required
@require_POST #check if this is needed - I think the if statement below makes it redundant
def upvote_book(request):

    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.upvote.filter(id=user.id).exists():
            # user has already upvoted this book
            # remove upvote
            book.upvote.remove(user)

        else:
            # add a new upvote for this website
            book.upvote.add(user)
            if book.downvote.filter(id=user.id).exists():
                book.downvote.remove(user)



    ctx = {'total_book_votes': book.total_votes,}
    return HttpResponse(book.total_votes)

@login_required
@require_POST
def downvote_book(request):

    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.downvote.filter(id=user.id).exists():
            # user has already downvoted this book
            # remove downvote
            book.downvote.remove(user)

        else:
            # add a new downvote for this website
            book.downvote.add(user)
            if book.upvote.filter(id=user.id).exists():
                book.upvote.remove(user)

    ctx = {'total_book_votes': book.total_votes}
    return HttpResponse(book.total_votes)

@login_required
@require_POST
def bookmark_book(request): #does this need to be ajax?

    if request.method == 'POST':
        user = request.user
        bookid = request.POST.get('bookid')
        book = BookRecommendation.objects.get(id=int(bookid))

        if book.bookmark.filter(id=user.id).exists():
            # user has already bookmarked this website
            # remove bookmark
            book.bookmark.remove(user)

        else:
            # add a new bookmark for this website
            book.bookmark.add(user)

    return HttpResponse(book.total_votes) #this should be changed - it doesnt need to respond with total votes

def book_comment(request, category_name_slug, subcategory_name_slug, pk):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
    user = request.user
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category'] = category
    subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
    context_dict['subcategory'] = subcategory
    book = get_object_or_404(BookRecommendation, id=pk)
    context_dict['book'] = book
    comments = BookComment.objects.filter(book=book).order_by('-created_date')[:100] #change the 100 so you can show unlimited comments
    context_dict['comments'] = comments


    if request.method == "POST" and request.user.is_authenticated:
        form = BookCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.author = user
            comment.save()
            return redirect('book_comment', category_name_slug=book.category.slug, subcategory_name_slug=book.subcategory.slug, pk=book.pk)

            #need an else here incase form is not valid

    else:
        form = BookCommentForm()
        context_dict['form'] = form

        return render(request, 'website/book_comment.html', context_dict)

class EditBookComment(UpdateView):
    model = BookComment
    form_class = BookCommentForm
    template_name = 'website/edit_book_comment.html'

    def get_context_data(self, **kwargs):
        context = super(EditBookComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = BookComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.book.category.slug
        subcategory_slug = self.object.book.subcategory.slug
        pk = self.object.book.pk
        return reverse('book_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})

class DeleteBookComment(DeleteView):
    model = BookComment
    template_name = 'website/delete_book_comment.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteBookComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = BookComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.book.category.slug
        subcategory_slug = self.object.book.subcategory.slug
        pk = self.object.book.pk
        return reverse('book_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})

@login_required
def create_video_recommendation(request, category_name_slug, subcategory_name_slug):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
    user = request.user
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category'] = category
    subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
    context_dict['subcategory'] = subcategory

    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            url = (form.cleaned_data['video_url'])
            video = form.save(commit=False)

            if url.startswith(('youtu', 'www')):
                url = 'http://' + url

            query = urlparse(url)

            if 'youtube' in query.hostname:
                if query.path == '/watch':
                    video_id= parse_qs(query.query)['v'][0]
                elif query.path.startswith(('/embed/', '/v/')):
                    video_id= query.path.split('/')[2]
            elif 'youtu.be' in query.hostname:
                video_id= query.path[1:]
            else:
                raise ValueError # change this to say - the video you supplied was not youtube

            DEVELOPER_KEY = os.environ['YOUTUBE_DEVELOPER_KEY']
            YOUTUBE_API_SERVICE_NAME = "youtube"
            YOUTUBE_API_VERSION = "v3"

            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)

            search_response = youtube.videos().list(
              id=video_id,
              part='snippet'
            ).execute()

            for item in search_response["items"]:
                title = item["snippet"]["title"]
                description = item["snippet"]["description"]
                thumbnail = item["snippet"]["thumbnails"]["standard"]["url"]
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
            return redirect('subcategory', category_name_slug=category.slug, subcategory_name_slug=subcategory.slug)
        else:
            #need to add proper handling of errors if they enter the wrong video url
            form = VideoForm()
            context_dict['form'] = form
            return render(request, 'website/create_video.html', context_dict)

    else:
        form = VideoForm()
        context_dict['form'] = form

        return render(request, 'website/create_video.html', context_dict)

class DeleteVideoRecommendation(DeleteView):
    model = VideoRecommendation
    template_name = 'website/delete_video.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteVideoRecommendation, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = VideoRecommendation.objects.get(pk=self.kwargs['pk'])
        if obj.recommended_by != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.category.slug
        subcategory_slug = self.object.subcategory.slug
        return reverse('subcategory', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug})

@login_required
@require_POST #check if this is needed - I think the if statement below makes it redundant
def upvote_video(request):

    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))

        if video.upvote.filter(id=user.id).exists():
            # user has already upvoted this book
            # remove upvote
            video.upvote.remove(user)

        else:
            # add a new upvote for this website
            video.upvote.add(user)
            if video.downvote.filter(id=user.id).exists():
                video.downvote.remove(user)



    ctx = {'total_video_votes': video.total_votes,}
    return HttpResponse(video.total_votes)

@login_required
@require_POST
def downvote_video(request):

    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))

        if video.downvote.filter(id=user.id).exists():
            # user has already downvoted this book
            # remove downvote
            video.downvote.remove(user)

        else:
            # add a new downvote for this website
            video.downvote.add(user)
            if video.upvote.filter(id=user.id).exists():
                video.upvote.remove(user)

    ctx = {'total_video_votes': video.total_votes}
    return HttpResponse(video.total_votes)

@login_required
@require_POST
def bookmark_video(request): #does this need to be ajax?

    if request.method == 'POST':
        user = request.user
        videoid = request.POST.get('videoid')
        video = VideoRecommendation.objects.get(id=int(videoid))

        if video.bookmark.filter(id=user.id).exists():
            # user has already bookmarked this video
            # remove bookmark
            video.bookmark.remove(user)

        else:
            # add a new bookmark for this video
            video.bookmark.add(user)

    return HttpResponse(video.total_votes) #this should be changed - it doesnt need to respond with total votes

def video_comment(request, category_name_slug, subcategory_name_slug, pk):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
    user = request.user
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category'] = category
    subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
    context_dict['subcategory'] = subcategory
    video = get_object_or_404(VideoRecommendation, id=pk)
    context_dict['video'] = video
    comments = VideoComment.objects.filter(video=video).order_by('-created_date')[:100] #change the 100 so you can show unlimited comments
    context_dict['comments'] = comments


    if request.method == "POST" and request.user.is_authenticated:
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = video
            comment.author = user
            comment.save()
            return redirect('video_comment', category_name_slug=video.category.slug, subcategory_name_slug=video.subcategory.slug, pk=video.pk)

            #need an else here incase form is not valid

    else:
        form = VideoCommentForm()
        context_dict['form'] = form

        return render(request, 'website/video_comment.html', context_dict)

class EditVideoComment(UpdateView):
    model = VideoComment
    form_class = VideoCommentForm
    template_name = 'website/edit_video_comment.html'

    def get_context_data(self, **kwargs):
        context = super(EditVideoComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = VideoComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.video.category.slug
        subcategory_slug = self.object.video.subcategory.slug
        pk = self.object.video.pk
        return reverse('video_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})

class DeleteVideoComment(DeleteView):
    model = VideoComment
    template_name = 'website/delete_video_comment.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteVideoComment, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('name')
        return context

    def get_object(self, queryset=None):
        obj = VideoComment.objects.get(pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        category_slug = self.object.video.category.slug
        subcategory_slug = self.object.video.subcategory.slug
        pk = self.object.video.pk
        return reverse('video_comment', kwargs={'category_name_slug': category_slug, 'subcategory_name_slug': subcategory_slug, 'pk': pk})
