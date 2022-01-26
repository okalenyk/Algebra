from logging import exception
from requests import (
    get as get_request,
    post as post_request,
)
from requests.exceptions import RequestException

from rest_framework.status import HTTP_200_OK

from backend.consts import REQUEST_ERROR


def send_get_request(url, params=None):
    response = get_request(url, params=params)

    if response.status_code != HTTP_200_OK:
        error_message = REQUEST_ERROR.format(
            f'URL \"{url}\" with params \"{params}\" isn\'t successfuly '
            f'responsed!\nRESPONSE STATUS CODE: \"{response.status_code}\".'
        )

        exception(error_message)

        raise RequestException(error_message)

    return response.json()


def send_post_request(url, params=None, json=None):
    response = post_request(url, params=params, json=json)

    if response.status_code != HTTP_200_OK:
        error_message = REQUEST_ERROR.format(
            f'URL \"{url}\" with params \"{params}\" isn\'t successfuly '
            f'responsed!\nRESPONSE STATUS CODE: \"{response.status_code}\".'
        )

        exception(error_message)

        raise RequestException(error_message)

    return response.json()
