from rest_framework import serializers
from uber.models import UberModel


class UberModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UberModel
        fields = ('email', 'access_token', 'name')

