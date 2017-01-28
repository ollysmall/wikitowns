from django.shortcuts import render
from django.http import HttpResponse
from website.models import Category

def index(request):
    category_list = Category.objects.all
    context_dict = {'categories': category_list}
    return render(request, 'website/index.html', context_dict)

def category(request, category_name_slug):
    category_list = Category.objects.all
    context_dict = {'categories': category_list}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    return render(request, 'website/category.html', context_dict)
