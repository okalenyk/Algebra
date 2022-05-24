import json
from smtplib import SMTPException

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.core.mail import send_mail
from django.conf import settings


class HealthcheckAPIView(GenericAPIView):
    serializer_class = None

    def _healcheck(self):
        return Response('I\'m alive!')

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request):
        return self._healcheck()


@csrf_exempt
@require_POST
def send_form_to_email(request):
    try:
        text = ''
        line = '%s: %s\n'

        data_json = json.loads(request.body)

        for key in data_json['data'].keys():
            text += line % (key, data_json['data'][key])

        send_mail(
            data_json['subject'],
            text,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_TO],
            fail_silently=False,
        )

        return JsonResponse({'message': 'successfully sent'}, status=200)
    except SMTPException as e:
        return JsonResponse({'message': 'Error sending email', 'error': str(e)}, status=500)
