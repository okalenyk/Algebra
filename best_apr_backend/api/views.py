import json
from smtplib import SMTPException

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
import base64


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

        mail = EmailMultiAlternatives(
            subject=data_json['subject'],
            body=text,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_TO]
        )

        try:
            image_id = 0
            for image_data in data_json['images']:
                image = MIMEImage(base64.b64decode(bytes(image_data, 'utf-8')))
                image.add_header('Content-ID', '<image-{}>'.format(image_id))

                mail.attach(image)
                image_id += 1
        except KeyError:
            pass
        except Exception as e:
            return JsonResponse({'message': 'Error with image processing', 'error': str(e)}, status=500)

        mail.send(fail_silently=False)

        return JsonResponse({'message': 'successfully sent'}, status=200)
    except SMTPException as e:
        return JsonResponse({'message': 'Error sending email', 'error': str(e)}, status=500)
