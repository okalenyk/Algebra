from rest_framework.response import Response
from rest_framework.generics import GenericAPIView


class HealthcheckAPIView(GenericAPIView):
    serializer_class = None

    def _healcheck(self):
        return Response('I\'m alive!')

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request):
        return self._healcheck()
