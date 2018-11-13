from rest_framework import serializers

from checkr.models import Audit


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'
        read_only_fields = ('report', 'status',)
