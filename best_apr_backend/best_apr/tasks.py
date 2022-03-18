from logging import exception

from backend.celery import app
from networks.models import Network
from .services.functions import update_pools_apr, update_eternal_farmings_apr, update_limit_farmings_apr


@app.task()
def update_pools_apr_task():
    for network in Network.objects.all():
        try:
            update_pools_apr(network)
        except Exception as exception_error:
            exception(
                f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
            )


@app.task()
def update_eternal_farmings_apr_task():
    for network in Network.objects.all():
        try:
            update_eternal_farmings_apr(network)
        except Exception as exception_error:
            exception(
                f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
            )


@app.task()
def update_limit_farmings_apr_task():
    for network in Network.objects.all():
        try:
            update_limit_farmings_apr(network)
        except Exception as exception_error:
            exception(
                f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
            )
