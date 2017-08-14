from website.models import Category

def category_context(request):
    return {'categories': Category.objects.order_by('name')}
    
