from django.conf import settings
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from checkr.models import Audit
from checkr.serializers import AuditSerializer
from checkr.utils import analyze_contract


class CheckrAPIView(CreateAPIView):
    serializer_class = AuditSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # temporarily run analyzer right away
        # TODO: Celery queue, find a good way to give result back
        try:
            audit_report = analyze_contract(request.data.get('contract'))
        except Exception as e:
            return Response(
                {'details': 'Something wrong happened, please try again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit_report.get('success'):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(audit_report, headers=headers,
                            status=status.HTTP_201_CREATED)

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
                if repo_audits.exists().result:
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
