"""wikitowns URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView
from website.forms import (MyCustomRegistrationForm, CustomPasswordResetForm,
                           CustomPasswordChangeForm, CustomSetPasswordForm)
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy


# redirects to home page after registration
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/'

urlpatterns = [
    url(r'', include('website.urls')),
    url(r'^accounts/register/$',
        MyRegistrationView.as_view(form_class=MyCustomRegistrationForm),
        name='registration_register'),  # redirects to index after registration
    url(r'^accounts/password/reset/$', auth_views.password_reset,
        {'post_reset_redirect': reverse_lazy('auth_password_reset_done'),
         'password_reset_form': CustomPasswordResetForm},
        name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': reverse_lazy('auth_password_reset_complete'),
         'set_password_form': CustomSetPasswordForm},
        name='auth_password_reset_confirm'),
    url(r'^accounts/password/change/$', auth_views.password_change,
        {'post_change_redirect': reverse_lazy('auth_password_change_done'),
         'password_change_form': CustomPasswordChangeForm},
        name='auth_password_change'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^admin/', admin.site.urls),
]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
