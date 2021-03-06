from django.urls import include, path
from django.views.generic import TemplateView

from checkr.api import BadgeAPIView, CheckrAPIView, GithubCheckrAPIView, ZipCheckrAPIView


api_urls = [
    path('badge/', BadgeAPIView.as_view()),
    path('audit/<str:tracking>/', CheckrAPIView.as_view()),
    path('audit/', CheckrAPIView.as_view()),
    path('github-audit/<str:tracking>/', GithubCheckrAPIView.as_view()),
    path('github-audit/', GithubCheckrAPIView.as_view()),
    path('zip-audit/<str:tracking>/', ZipCheckrAPIView.as_view()),
    path('zip-audit/', ZipCheckrAPIView.as_view()),
]

urlpatterns = [
    path('api/', include(api_urls)),
    path('github-audit/', TemplateView.as_view(template_name="github.html")),
    path('', TemplateView.as_view(template_name="index.html")),
]
