from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/(?P<username>\w+)/$', views.profile_page, name='user_profile'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category,
        name='category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/$', views.subcategory,
        name='subcategory'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/new_website/$',
        login_required(views.CreateWebsiteRecommendation.as_view()),
        name='create_website'),
    url(r'^delete_website/(?P<pk>\d+)/$',
        login_required(views.DeleteWebsiteRecommendation.as_view()),
        name='delete_website'),
    url(r'^upvote_website/$', views.upvote_website, name='upvote_website'),
    url(r'^downvote_website/$', views.downvote_website,
        name='downvote_website'),
    url(r'^bookmark_website/$', views.bookmark_website,
        name='bookmark_website'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/comments/$',
        views.website_comment, name='website_comment'),
    url(r'^delete_website_comment/(?P<pk>\d+)/$',
        login_required(views.DeleteWebsiteComment.as_view()),
        name='delete_website_comment'),
    url(r'^edit_website_comment/(?P<pk>\d+)/$',
        login_required(views.EditWebsiteComment.as_view()),
        name='edit_website_comment'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/new_book/$',
        views.create_book_recommendation, name='create_book'),
    url(r'^delete_book/(?P<pk>\d+)/$',
        login_required(views.DeleteBookRecommendation.as_view()),
        name='delete_book'),
    url(r'^upvote_book/$', views.upvote_book, name='upvote_book'),
    url(r'^downvote_book/$', views.downvote_book, name='downvote_book'),
    url(r'^bookmark_book/$', views.bookmark_book, name='bookmark_book'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/book_comments/$',
        views.book_comment, name='book_comment'),
    url(r'^delete_book_comment/(?P<pk>\d+)/$',
        login_required(views.DeleteBookComment.as_view()),
        name='delete_book_comment'),
    url(r'^edit_book_comment/(?P<pk>\d+)/$',
        login_required(views.EditBookComment.as_view()),
        name='edit_book_comment'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/new_video/$',
        views.create_video_recommendation, name='create_video'),
    url(r'^delete_video/(?P<pk>\d+)/$',
        login_required(views.DeleteVideoRecommendation.as_view()),
        name='delete_video'),
    url(r'^upvote_video/$', views.upvote_video, name='upvote_video'),
    url(r'^downvote_video/$', views.downvote_video, name='downvote_video'),
    url(r'^bookmark_video/$', views.bookmark_video, name='bookmark_video'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/video_comments/$',
        views.video_comment, name='video_comment'),
    url(r'^delete_video_comment/(?P<pk>\d+)/$',
        login_required(views.DeleteVideoComment.as_view()),
        name='delete_video_comment'),
    url(r'^edit_video_comment/(?P<pk>\d+)/$',
        login_required(views.EditVideoComment.as_view()),
        name='edit_video_comment'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/'
        r'report_website_recommendation/$',
        views.report_website_recommendation,
        name='report_website_recommendation'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/'
        r'report_book_recommendation/$', views.report_book_recommendation,
        name='report_book_recommendation'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/'
        r'(?P<subcategory_name_slug>[\w\-]+)/(?P<pk>\d+)/'
        r'report_video_recommendation/$', views.report_video_recommendation,
        name='report_video_recommendation'),
    url(r'^icons/$', views.icons, name='icons'),
]
