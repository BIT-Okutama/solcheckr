from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from checkr.serializers import AuditSerializer
from checkr.utils import analyze_contract


class CheckrAPIView(CreateAPIView):
    serializer_class = AuditSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # temporarily run analyzer right away
        # TODO: Only analyze if Solidity code has no errors
        # TODO: Celery queue, find a good way to give result back
        try:
            audit_report = analyze_contract(request.data.get('contract'))
        except Exception as e:
            return Response(
                {'details': 'Something wrong happened, please try again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(audit_report,
                        status=status.HTTP_201_CREATED, headers=headers)
