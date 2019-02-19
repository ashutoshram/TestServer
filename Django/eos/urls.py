from django.conf.urls import url
from django.conf import settings 
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^upload/', views.test_upload, name='test_upload'),
    url(r'^success/$', views.upload_success, name='upload_success')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
