from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/(?P<username>\w+)/$', views.profile_page, name='user_profile'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/$', views.subcategory, name='subcategory'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/new_website/$', login_required(views.CreateWebsiteRecommendation.as_view()), name='create_website'),
    url(r'^delete_website/(?P<pk>\d+)/$', login_required(views.DeleteWebsiteRecommendation.as_view()), name='delete_website'),
    url(r'^upvote_website/$', views.upvote_website, name='upvote_website'),
    url(r'^downvote_website/$', views.downvote_website, name='downvote_website'),
    url(r'^bookmark_website/$', views.bookmark_website, name='bookmark_website'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/comments/$', views.website_comment, name='website_comment'),
    url(r'^delete_website_comment/(?P<pk>\d+)/$', login_required(views.DeleteWebsiteComment.as_view()), name='delete_website_comment'),
    url(r'^edit_website_comment/(?P<pk>\d+)/$', login_required(views.EditWebsiteComment.as_view()), name='edit_website_comment'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<subcategory_name_slug>[\w\-]+)/new_book/$', views.create_book_recommendation, name='create_book'),
    url(r'^delete_book/(?P<pk>\d+)/$', login_required(views.DeleteBookRecommendation.as_view()), name='delete_book'),
]
