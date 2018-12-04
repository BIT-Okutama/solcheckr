import ast
import re

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from checkr.models import Audit, GithubAudit
from checkr.serializers import AuditSerializer, GithubAuditSerializer
from checkr.utils import analyze_contract, analyze_repository


class CheckrAPIView(CreateAPIView):
    lookup_field = 'tracking'
    lookup_url_kwarg = 'tracking'
    queryset = Audit.objects
    serializer_class = AuditSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, tracking=self.kwargs.get('tracking'))
        serializer = self.get_serializer(instance)
        response = serializer.data
        if response.get('report'):
            response.update({'report': ast.literal_eval(response.get('report'))})
        return Response(response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            audit_report = analyze_contract(request.data.get('contract'))
        except Exception as e:
            return Response(
                {'details': 'Something wrong happened, please try again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit_report.get('success'):
            passed_test = True  # passed or failed test
            for issue in audit_report.get('issues'):
                if issue.get('severity') < 3:
                    passed_test = False
                    break

            serializer.save(
                report=str(audit_report.get('issues')),
                result=passed_test
            )
            headers = self.get_success_headers(serializer.data)
            audit_report.update({'tracking': serializer.instance.tracking})

            return Response(audit_report, headers=headers,
                            status=status.HTTP_201_CREATED)

        return Response(audit_report, status=status.HTTP_400_BAD_REQUEST)


class GithubCheckrAPIView(GenericAPIView):
    lookup_field = 'tracking'
    lookup_url_kwarg = 'tracking'
    queryset = GithubAudit.objects
    serializer_class = GithubAuditSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, tracking=self.kwargs.get('tracking'))
        serializer = self.get_serializer(instance)
        response = serializer.data
        if response.get('report'):
            response.update({'report': ast.literal_eval(response.get('report'))})
            response.update({'contracts': ast.literal_eval(response.get('contracts'))})
        return Response(response)

    def post(self, request, *args, **kwargs):
        github_repo = ''
        if request.data.get('repository_url'):
            repo_regex = r'^(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$'
            match_url = re.match(repo_regex, request.data.get('repository_url'))

            if not match_url:
                return Response(
                    {'details': 'The provided GitHub repository URL is invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            url_tokens = match_url.groups()
            github_repo = '/'.join([x for x in url_tokens[len(url_tokens) - 2:]])

        try:
            audit_report = analyze_repository(github_repo)
        except Exception as e:
            return Response(
                {'details': 'Something wrong happened, please try again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit_report.get('success'):
            return Response(audit_report, status=status.HTTP_201_CREATED)

        return Response(audit_report, status=status.HTTP_400_BAD_REQUEST)


class BadgeAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        github_user = request.query_params.get('user')
        github_repo = request.query_params.get('repo')
        file_name = 'fund-me.svg'

        if github_user and github_repo:
            repo_audits = Audit.objects.filter(
                github_user=github_user, github_repo=github_repo
            )
            if repo_audits.exists():
                if repo_audits.last().result:
                    file_name = 'passed.svg'
                else:
                    file_name = 'failed.svg'

            # Improve this implementation
            badge_file = open(
                '{}/images/{}'.format(settings.STATICFILES_DIRS[0], file_name),
                'rb'
            )
            response = HttpResponse(content=badge_file)
            response['Content-Type'] = 'image/svg+xml'
            return response

        return Response({
            'details': 'Include GitHub username and repository in URL parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
