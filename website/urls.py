from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/$', views.subcategory, name='subcategory'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/new_website/$', login_required(views.CreateWebsiteRecommendation.as_view()), name='create_website'),
    url(r'^delete_website/(?P<pk>\d+)/$', login_required(views.DeleteWebsiteRecommendation.as_view()), name='delete_website'),
]
