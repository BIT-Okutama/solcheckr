from rest_framework import serializers

from checkr.models import Audit, GithubAudit


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'
        read_only_fields = ('report', 'result', 'tracking',)


class GithubAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubAudit
        fields = '__all__'
        read_only_fields = ('contracts', 'report', 'result', 'tracking',)
