from logging import exception
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ReadTimeout,
    SSLError,
)
from typing import Union

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.exceptions import TransactionNotFound

from backend.consts import NETWORK_ERROR
from ..exceptions import ProviderNotConnected


def check_address_is_checksum_format(address: str) -> bool:
    return Web3.isChecksumAddress(address)


def convert_to_checksum_address_format(
    address: Union[str, ChecksumAddress]
) -> ChecksumAddress:
    if not check_address_is_checksum_format(address):
        return Web3.toChecksumAddress(address)

    return address


def reset_connection(function):
    """
    Decorator for handling connection error to RPC provider and switching
    to the next url for success connection
    """

    def wrapped(*args, **kwargs):
        try:
            result = function(*args, **kwargs)

            return result
        except (
                ProviderNotConnected,
                ReadTimeout,
                HTTPError,
                ConnectionError,
                SSLError,
        ) as exception_error:
            exception(NETWORK_ERROR.format(exception_error))

            args = list(args)
            custom_rpc_provider = args[0]

            rpc_url_list = custom_rpc_provider.network.rpc_url_list

            if custom_rpc_provider.url_number + 1 >= len(rpc_url_list):
                custom_rpc_provider.url_number = 0

                raise exception_error

            # Switch to the next rpc provider and try again
            custom_rpc_provider.url_number += 1

            args[0] = custom_rpc_provider

            return wrapped(*args, **kwargs)

    return wrapped
