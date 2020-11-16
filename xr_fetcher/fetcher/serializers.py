import json
from rest_framework import serializers

class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    description = serializers.CharField()

class RateSerializer(serializers.Serializer):
    value = serializers.FloatField()
    last_updated = serializers.DateTimeField()
    status = SuccessSerializer()

class FullRatesSerializer(serializers.Serializer):
    dof = RateSerializer()
    fixer = RateSerializer()
    banxico = RateSerializer()

class WrappedRatesSerializer(serializers.Serializer):
    rates = FullRatesSerializer()

