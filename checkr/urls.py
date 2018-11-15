from django.urls import include, path
from django.views.generic import TemplateView

from checkr.api import BadgeAPIView, CheckrAPIView


api_urls = [
    path('badge/', BadgeAPIView.as_view()),
    path('audit/', CheckrAPIView.as_view()),
]

urlpatterns = [
    path('api/', include(api_urls)),
    path('', TemplateView.as_view(template_name="index.html"))
]
