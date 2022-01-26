from logging import exception, info, warn, warning
from operator import contains
from typing import List, Tuple
from copy import deepcopy
import weakref

from django.conf import settings
from django.db import router
from decimal import *
from eth_utils import to_bytes
from eth_utils.hexadecimal import add_0x_prefix, remove_0x_prefix
from web3.exceptions import ContractLogicError
from web3.types import HexStr

from backend.consts import DEFAULT_CRYPTO_ADDRESS
from blockchain_explorers.models import (
    EtherscanLikeBlockchainExplorer,
    RequestToEtherscanLikeAPI,
)
from contracts.models import Contract, TokenContract
from networks.exceptions import TransactionReverted
from networks.models import Network, CustomRpcProvider, Transaction
from networks.services.functions import convert_to_checksum_address_format
from base.requests import send_get_request
from tokens.models import Token
from web3.exceptions import (
    TimeExhausted,
    TransactionNotFound
)


tokens = [
    {"address": '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270', "symbol": 'WMATIC'},
    {"address": '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619', "symbol": 'WETH'},
    {"address": '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063', "symbol": 'DAI'},
    {"address": '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', "symbol": 'USDT'},
    {"address": '0x2791bca1f2de4661ed88a30c99a7a9449aa84174', "symbol": 'USDC'},
    {"address": '0x831753DD7087CaC61aB5644b308642cc1c33Dc13', "symbol": 'QUICK'}
]


# def get_gas_volume(contract_function, from_address):
#     try:
#         gas_volume = contract_function.estimateGas(
#             {
#                 'from': convert_to_checksum_address_format(from_address)
#             }
#         )
#     except Exception as exception_error:
#         exception(exception_error)
#
#         gas_volume = settings.DEFAULT_GAS_VOLUME
#
#     return int(gas_volume * settings.DEFAULT_GAS_VOLUME_INCREASE_PERCENT)


# def check_transaction_status(
#     contract: Contract,
#     transaction_hash: str,
# ):
#     info(f"Checking status of transaction with hash \"{transaction_hash}\"")
#     try:
#         if not Transaction.get_transaction_status(
#             CustomRpcProvider(contract.network),
#             transaction_hash,
#         ):
#             exception(f"Transaction with hash \"{transaction_hash}\" reverted")
#             raise TransactionReverted()
#         else:
#             return True
#     except TimeExhausted as exception_error:
#         raise TransactionNotFound(
#             f'Transaction with the \"{transaction_hash}\" not found'
#             ' within a specified time!',
#         ) from exception_error


# def get_route_amount(
#     route: str,
#     amount: int,
#     algebra_quote_contract,
# ):
#     try:
#         print(route, amount)
#         amount = algebra_quote_contract.load_contract().functions.quoteExactInput(
#             route,
#             amount,
#         ).call()[0]
#     except ContractLogicError as exception_error:
#         print(exception_error)
#
#         amount = 0
#
#     return amount


# def get_all_possible_routes(
#     max_hops: int,
# ):
#     routes = list()
#
#     for token in tokens:
#         routes.append(remove_0x_prefix(convert_to_checksum_address_format(
#             address=token.get('address', ''))
#         ))
#
#     max_hops -= 1
#
#     for _ in range(max_hops):
#         new_routes = list()
#         for token in tokens:
#             for route in routes:
#                 new_routes.append(route + remove_0x_prefix(convert_to_checksum_address_format(
#                     address=token.get('address', '')
#                 )))
#
#         routes += new_routes
#
#     return set(routes)


# def get_best_not_single_route(
#     algebra_quote_contract,
#     from_token_address: str,
#     to_token_address: str,
#     amount: int,
#     max_hops: int,
# ):
#     best_route = ''
#     best_amount = 0
#
#     for route in get_all_possible_routes(max_hops=max_hops):
#         full_route = f"{from_token_address}{route}{to_token_address[2:]}"
#
#         new_amount = get_route_amount(
#             route=full_route,
#             amount=amount,
#             algebra_quote_contract=algebra_quote_contract,
#         )
#
#         if new_amount > best_amount:
#             best_amount = new_amount
#             best_route = full_route
#
#     return best_route, best_amount


# def get_best_route(
#     quote_contract,
#     from_token_address: HexStr,
#     to_token_address: HexStr,
#     amount: int,
#     max_hops: int = settings.DEFAULT_MAX_HOPS,
# ):
#     try:
#         single_route_amount = quote_contract.load_contract().functions.quoteExactInputSingle(
#             convert_to_checksum_address_format(from_token_address),
#             convert_to_checksum_address_format(to_token_address),
#             amount,
#             0,
#         ).call()[0]
#
#         best_route = {
#             'from_token': from_token_address,
#             'to_token': to_token_address,
#             'amount': single_route_amount,
#             'path': f'0x{remove_0x_prefix(from_token_address)}{remove_0x_prefix(to_token_address)}'
#         }
#     except ContractLogicError:
#         best_route = {
#             'from_token': from_token_address,
#             'to_token': to_token_address,
#             'amount': 0,
#             'path': '',
#         }
#
#     max_hops -= 1
#
#     best_not_single_route, not_single_amount = get_best_not_single_route(
#         algebra_quote_contract=quote_contract,
#         from_token_address=from_token_address,
#         to_token_address=to_token_address,
#         amount=amount,
#         max_hops=max_hops,
#     )
#
#     if best_route.get('amount') < not_single_amount:
#         best_route['amount'] = not_single_amount
#         best_route['path'] = best_not_single_route
#
#     return best_route


# def check_gas_price(
#     gas_price,
#     min_gas_price,
# ):
#     if gas_price < min_gas_price:
#         warning(
#             f'Low gas price from blockchain: \"{gas_price=}\". Will be used'
#             f' minimum gas price by contract: \"{min_gas_price=}\".'
#         )
#
#         return min_gas_price
#     return gas_price


# def build_transaction(custom_rpc_provider: CustomRpcProvider, contract_function):
#     try:
#         # gas_price = send_get_request(settings.GAS_STATION_MATIC).get(
#         #     "standard", custom_rpc_provider.get_gas_price())
#         # if not gas_price:
#         gas_price = custom_rpc_provider.get_gas_price()
#     except Exception as e:
#         exception(f"Error fetching from Gas Station Matic API: {e}")
#         gas_price = custom_rpc_provider.get_gas_price()
#
#     info(f"Gas price from rpc: {gas_price}")
#     gas_price = check_gas_price(gas_price, settings.DEFAULT_MIN_GAS_PRICE)
#     info(f"Gas price after check: {gas_price}")
#
#     initilized_transaction = contract_function.buildTransaction(
#         {
#             'from': convert_to_checksum_address_format(
#                 settings.VAULT_OWNER_ADDRESS),
#             'nonce': custom_rpc_provider.get_transaction_count(
#                 convert_to_checksum_address_format(
#                     settings.VAULT_OWNER_ADDRESS),
#             ),
#             'gasPrice': int(gas_price * settings.DEFAULT_INCREASING_PERCENT),
#             'gas': get_gas_volume(
#                 contract_function=contract_function,
#                 from_address=settings.VAULT_OWNER_ADDRESS,
#             ),
#         }
#     )
#
#     return initilized_transaction


# def increase_gas_price(gas_price):
#     gas_price *= Decimal(settings.DEFAULT_INCREASING_PERCENT)
#     gas_price = int(Decimal(gas_price).quantize(Decimal('1'), ROUND_HALF_UP))
#     return gas_price


# def initialize_and_build_tx(
#     custom_rpc_provider: CustomRpcProvider,
#     contract_function,
#     vault_contract,
#     tx_params: dict,
#     counter: int,
# ):
#     if counter > settings.DEFAULT_SPEED_UP_COUNTER:
#         warning(f"Attempts of speed-up {settings.DEFAULT_SPEED_UP_COUNTER}x failed")
#         return
#
#     counter += 1
#     info(f"Attempts of building tx {counter} time")
#
#     initilized_transaction = contract_function.buildTransaction(tx_params)
#
#     signed_transaction = custom_rpc_provider.sign_transaction(
#         transaction=initilized_transaction,
#         private_key=settings.VAULT_OWNER_PRIVATE_KEY,
#     )
#
#     transaction = custom_rpc_provider.send_raw_transaction(
#         signed_transaction=signed_transaction.rawTransaction,
#     )
#
#     try:
#         if check_transaction_status(
#             contract=vault_contract,
#             transaction_hash=transaction
#         ):
#             stacking_transaction = Transaction(
#                 hash=transaction.hex(),
#                 network=vault_contract.network,
#             )
#
#             stacking_transaction.save()
#     except TransactionNotFound as e:
#         warning(f"Transaction not found: {e}")
#
#         gas_price = tx_params["gasPrice"]
#         tx_params.update(gasPrice=increase_gas_price(gas_price))
#
#         transaction = initialize_and_build_tx(
#             custom_rpc_provider=custom_rpc_provider,
#             contract_function=contract_function,
#             vault_contract=vault_contract,
#             tx_params=tx_params,
#             counter=counter,
#         )
#
#     return transaction


# def check_new_entires(
#     blockchain_name: str,
#     address: str = settings.POLYGON_VAULT_CONTRACT
# ):
#     blockchain_name = blockchain_name.strip().lower()
#     address = address.strip().lower()
#     block_step = settings.DEFAULT_SCAN_BLOCK_RANGE
#     network = Network.displayed_objects.filter(
#         title=blockchain_name).first()
#
#     custom_rpc_provider = CustomRpcProvider(network)
#
#     last_check = RequestToEtherscanLikeAPI.get_last_response(
#         blockchain_name=blockchain_name,
#         address=address,
#     )
#
#     if not last_check:
#         info("Last request to eth-like api not found")
#         from_block = settings.DEFAULT_START_SCAN_BLOCK
#     else:
#         from_block = last_check.from_block
#
#     tokens_response = list()
#     try:
#         last_block = custom_rpc_provider.get_current_block_number()
#         while last_block > from_block:
#             to_block = from_block + block_step
#             new_check, created = RequestToEtherscanLikeAPI.create(
#                 blockchain_explorer_id=EtherscanLikeBlockchainExplorer.objects.filter(
#                     network__title__iexact=network.title,
#                 ).first().id,
#                 address=address,
#                 from_block=from_block,
#                 to_block=to_block,
#             )
#             from_block = to_block + 1
#             if created:
#                 info(f"Request to eth-like api was created: {new_check}")
#                 tokens_response += new_check.response.get("result")
#     except Exception as exception_error:
#         exception(exception_error)
#
#     if not tokens_response:
#         return
#
#     vault_contract = Contract.get_contract_by_address(
#         network_id=network.id,
#         address=settings.POLYGON_VAULT_CONTRACT,
#     )
#
#     algebra_token = Token.get_token(
#         network.id, settings.ALGB_CONTRACT
#     )
#
#     quote_contract = Contract.get_contract_by_address(
#         network_id=network.id,
#         address=settings.ALGEBRA_QUOTE_CONTRACT,
#     )
#
#     processed_tokens = set()
#
#     for token_response in tokens_response:
#         if not isinstance(token_response, dict):
#             continue
#
#         if token_response.get("contractAddress") not in processed_tokens:
#             processed_tokens.add(token_response.get("contractAddress"))
#
#     for token_address in processed_tokens:
#         if token_address.lower() == algebra_token.address.lower():
#             continue
#
#         token = Token.get_token(
#             network_id=network.id,
#             address=token_address,
#         )
#
#         token_contract = TokenContract \
#             .get_contract_by_address(network.id, DEFAULT_CRYPTO_ADDRESS) \
#             .load_contract(address=convert_to_checksum_address_format(token.address))
#
#         token_balance = token_contract.functions.balanceOf(
#             convert_to_checksum_address_format(
#                 address=vault_contract.address,
#             )
#         ).call()
#
#         if token_balance <= 0:
#             continue
#
#         best_route = get_best_route(
#             quote_contract=quote_contract,
#             from_token_address=convert_to_checksum_address_format(
#                 address=token.address,
#             ),
#             to_token_address=convert_to_checksum_address_format(
#                 address=algebra_token.address,
#             ),
#             amount=token_balance,
#         )
#
#         amount_with_slippage = int(best_route.get(
#             'amount', 0) * (1 - token.slippage))
#
#         if amount_with_slippage < settings.TOKEN_MIN_VALUE * 10**algebra_token.decimals:
#             continue
#
#         try:
#             contract_function = vault_contract.load_contract().functions.swapToALGB(
#                 tokenToSwap=convert_to_checksum_address_format(token.address),
#                 path=best_route.get('path', ''),
#                 amountOutMin=amount_with_slippage,
#                 withFee=int(token.is_deflation),
#             )
#         except Exception as e:
#             warning(f"Can't swap token to ALGB: {e}")
#             continue
#
#         custom_rpc_provider = CustomRpcProvider(
#             network=vault_contract.network,
#         )
#
#         try:
#             initilized_transaction = build_transaction(
#                 custom_rpc_provider=custom_rpc_provider,
#                 contract_function=contract_function,
#             )
#         except Exception as e:
#             warning(f"Can't build transaction: {e}")
#             continue
#
#         signed_transaction = custom_rpc_provider.sign_transaction(
#             transaction=initilized_transaction,
#             private_key=settings.VAULT_OWNER_PRIVATE_KEY,
#         )
#
#         transaction = custom_rpc_provider.send_raw_transaction(
#             signed_transaction=signed_transaction.rawTransaction,
#         )
#
#         if check_transaction_status(
#             contract=vault_contract,
#             transaction_hash=transaction
#         ):
#             stacking_transaction = Transaction(
#                 hash=transaction.hex(),
#                 network=vault_contract.network,
#             )
#
#             stacking_transaction.save()

    # algebra_token_contract = TokenContract\
    #     .get_contract_by_address(network.id, DEFAULT_CRYPTO_ADDRESS)\
    #     .load_contract(address=convert_to_checksum_address_format(algebra_token.address))

    # vault_algebra_balance = algebra_token_contract.functions.balanceOf(
    #     convert_to_checksum_address_format(
    #         address=vault_contract.address,
    #     )
    # ).call()

    # if vault_algebra_balance < settings.TOKEN_MIN_VALUE * 10 ** algebra_token.decimals:
    #     exception(f"Current Algebra balance lesser than minim value\n"
    #               f"Current balance: {vault_algebra_balance}\n"
    #               f"Min value: {settings.TOKEN_MIN_VALUE * 10 ** algebra_token.decimals}")

    #     return

    # contract_function = vault_contract.load_contract().functions.transferALGB(
    #     int(100 * settings.PERCENT_TO_TRANSFER),
    # )

    # try:
    #     initilized_transaction = build_transaction(
    #         custom_rpc_provider=custom_rpc_provider,
    #         contract_function=contract_function,
    #     )
    # except Exception as e:
    #     warning(f"Can't build transaction: {e}")

    # signed_transaction = custom_rpc_provider.sign_transaction(
    #     transaction=initilized_transaction,
    #     private_key=settings.VAULT_OWNER_PRIVATE_KEY,
    # )

    # transaction = custom_rpc_provider.send_raw_transaction(
    #     signed_transaction=signed_transaction.rawTransaction,
    # )

    # if check_transaction_status(
    #     contract=vault_contract,
    #     transaction_hash=transaction
    # ):
    #     stacking_transaction = Transaction(
    #         hash=transaction.hex(),
    #         network=vault_contract.network,
    #     )

    #     stacking_transaction.save()


# def transfer_algb_to_stacking(
#     blockchain_name: str,
# ):
#     blockchain_name = blockchain_name.strip().lower()
#     network = Network.displayed_objects.filter(
#         title=blockchain_name).first()
#
#     vault_contract = Contract.get_contract_by_address(
#         network_id=network.id,
#         address=settings.POLYGON_VAULT_CONTRACT,
#     )
#
#     info(f"Vault contract was found {vault_contract.address}")
#     try:
#         contract_function = vault_contract.load_contract().functions.transferALGBToStaking()
#     except Exception as e:
#         warning(f"Can't transfer algn to staking: {e}")
#
#     custom_rpc_provider = CustomRpcProvider(
#         network=vault_contract.network,
#     )
#
#     try:
#         gas_price = custom_rpc_provider.get_gas_price()
#     except Exception as e:
#         exception(f"Error fetching from Gas Station Matic API: {e}")
#         gas_price = custom_rpc_provider.get_gas_price()
#
#     tx_params = {
#         'from': convert_to_checksum_address_format(
#             settings.VAULT_OWNER_ADDRESS),
#         'nonce': custom_rpc_provider.get_transaction_count(
#             convert_to_checksum_address_format(
#                 settings.VAULT_OWNER_ADDRESS),
#         ),
#         'gasPrice': int(gas_price * settings.DEFAULT_INCREASING_PERCENT),
#         'gas': get_gas_volume(
#             contract_function=contract_function,
#             from_address=settings.VAULT_OWNER_ADDRESS,
#         ),
#     }
#
#     transaction = initialize_and_build_tx(
#         custom_rpc_provider=custom_rpc_provider,
#         contract_function=contract_function,
#         vault_contract=vault_contract,
#         tx_params=tx_params,
#         counter=0,
#     )
#     if transaction:
#         info(f"Transfer ALGB to stacking: {transaction} was successfully created!")
#     else:
#         warning(f"Error creating transfer to stacking")
