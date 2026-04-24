from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import capture_image, VideoCaptureView
from .views import (
    SensorDataViewSet, VideoCaptureView, home, stream_lidar,
    record_lidar_dataset, list_lidar_datasets, download_lidar_file,
    create_image_dataset_stream, download_image_dataset, download_video_dataset,
    video, video_feed
)

router = DefaultRouter()
router.register(r'sensor-data', SensorDataViewSet, basename='sensor-data')

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
    path('api/capture-image/', capture_image, name='capture_image'),
    path('api/video-capture/', VideoCaptureView.as_view(), name='video-capture'),
    path('api/create-image-dataset-stream/', create_image_dataset_stream, name='create-image-dataset-stream'),
    path('api/download-image-dataset/', download_image_dataset, name='download-image-dataset'),
    path('video/', video, name='video'),
    path('api/video-feed/', video_feed, name='video-feed'),
    path('api/download-video-dataset/', download_video_dataset, name='download-video-dataset'),
    path('api/stream-lidar/', stream_lidar, name='stream-lidar'),
    path('api/record-lidar-dataset/', record_lidar_dataset, name='record-lidar-dataset'),
    path('api/list-lidar-datasets/', list_lidar_datasets, name='list-lidar-datasets'),
    path('api/download-lidar-file/<str:filename>/', download_lidar_file, name='download-lidar-file'),

]

# Geliştirme ortamında medya dosyalarını servis etmek için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)