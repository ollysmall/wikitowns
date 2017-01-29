from django.shortcuts import render
from django.http import HttpResponse
from website.models import Category, SubCategory

def index(request):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}
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
        subcategory = SubCategory.objects.get(slug=subcategory_name_slug)
        context_dict['subcategory_name'] = subcategory.name
        context_dict['subcategory'] = subcategory
    except SubCategory.DoesNotExist:
        pass

    return render(request, 'website/subcategory.html', context_dict)
