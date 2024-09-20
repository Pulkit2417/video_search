from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('search/<int:video_id>/', views.search_subtitles, name='search_subtitles'),
    path('play/<int:video_id>/', views.play_video, name='video_play'),
    path('list/', views.video_list, name='video_list'),  # Ensure this exists or adjust as needed
]
