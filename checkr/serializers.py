from rest_framework import serializers

from checkr.models import Audit


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'
        read_only_fields = ('report', 'result', 'status',)

    def validate(self, data):
        """Check that either email address or GitHub info is provided"""
        if not data.get('email') and not data.get('github_username'):
            raise serializers.ValidationError(
                'Please provide an email address or GitHub details'
            )

        incomplete_github = ((data.get('github_user') and not data.get('github_repo')) or
                             (data.get('github_repo') and not data.get('github_user')))

        if incomplete_github:
            raise serializers.ValidationError(
                'Please provide both GitHub username and repository'
            )
        return data
