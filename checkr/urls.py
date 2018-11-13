from django.urls import include, path

from checkr.api import CheckrAPIView


api_urls = [
    path('audit/', CheckrAPIView.as_view()),
]

urlpatterns = [
    path('api/', include(api_urls)),
]
