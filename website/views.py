from django.shortcuts import render
from django.http import HttpResponse, Http404
from website.models import Category, SubCategory, WebsiteRecommendation
from website.forms import WebsiteForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

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
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category'] = category
        subcategory = SubCategory.objects.get(slug=subcategory_name_slug, category=category)
        context_dict['subcategory_name'] = subcategory.name
        context_dict['subcategory'] = subcategory
        website_list = WebsiteRecommendation.objects.filter(subcategory=subcategory).order_by('-created_date')
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
