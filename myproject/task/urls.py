from django.urls import path, include

from task import views
urlpatterns = [
  path('upload/', views.UploadFile.as_view(), name='upload-file'),
]
