from django.conf.urls import url
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^success/$', views.upload_success, name='upload_success'),
    url(r'^progress/$', views.progress, name="progress"),
    path('create_suite/', views.create_suite, name='create_suite'),
    path('upload/', views.test_upload, name='test_upload'),
    path('run_test/<uuid:test_id>', views.run_test, name='run_test'),
    path('edit_test/<uuid:test_id>', views.edit_test, name='edit_test'),
    path('run_test/report/<uuid:report_id>', views.report, name='report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
