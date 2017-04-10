from django.shortcuts import render
from django.http import HttpResponse, Http404
from website.models import Category, SubCategory, WebsiteRecommendation, WebsiteComment
from website.forms import WebsiteForm, WebsiteCommentForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt #get rid of this
from django.db.models import Count

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

    except SubCategory.DoesNotExist:
        pass

    return render(request, 'website/subcategory.html', context_dict)

class CreateWebsiteRecommendation(CreateView):
    model = WebsiteRecommendation
    form_class = WebsiteForm
    template_name = 'website/create_website.html'

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
    website_bookmarks = WebsiteRecommendation.objects.filter(bookmark=user).order_by('-created_date')[:100] #change the 100 so you can show unlimited recomendations
    context_dict['website_bookmarks'] = website_bookmarks
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
    comments = WebsiteComment.objects.filter(website=website).order_by('created_date')[:100] #change the 100 so you can show unlimited comments
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
