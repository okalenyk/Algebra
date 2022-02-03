from logging import exception

from backend.celery import app
from .services.functions import update_pools_apr


@app.task()
def update_pools_apr_task():
    try:
        update_pools_apr()
    except Exception as exception_error:
        exception(
            f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
        )
