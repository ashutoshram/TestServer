from django.conf.urls import url
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^upload/', views.test_upload, name='test_upload'),
    url(r'^success/$', views.upload_success, name='upload_success'),
    path('get_arguments/<uuid:test_id>', views.get_arguments, name='get_arguments'),
    path('edit_test/<uuid:test_id>', views.edit_test, name='edit_test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
