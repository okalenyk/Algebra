from logging import exception

from backend.celery import app
from .services.functions import update_positions_last_fee_growth


@app.task()
def update_positions_last_fee_growth_task():
    try:
        update_positions_last_fee_growth()
    except Exception as exception_error:
        exception(
            f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
        )
