import logging

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

#from . import serializers

log = logging.getLogger(__name__)

class HelloWorld(APIView):
    permission_classes = [ TokenHasReadWriteScope ]
    def get(self, request, format=None):
        log.info("Hello")
        return Response({"message": "Hello, world!"})
