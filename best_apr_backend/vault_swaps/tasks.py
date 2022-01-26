from logging import exception

from backend.celery import app
from .services.functions import check_new_entires, transfer_algb_to_stacking


# @app.task()
# def scan_polygon_vault_contract_task():
#     try:
#         check_new_entires("polygon")
#     except Exception as exception_error:
#         exception(
#             f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
#         )


@app.task()
def transfer_algb_to_stacking_task():
    try:
        transfer_algb_to_stacking("polygon")
    except Exception as exception_error:
        exception(
            f'~~~~~~~~~~~~~~~\n{exception_error}\n~~~~~~~~~~~~~~~'
        )
