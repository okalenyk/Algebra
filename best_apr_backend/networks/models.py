from logging import exception, warning, info
from typing import Union
from uuid import UUID

from django.conf import settings
from django.db.models import (
    CharField,
    DecimalField,
    ForeignKey,
    JSONField,
    PositiveIntegerField,
    PROTECT,
    URLField,
)
from eth_utils import add_0x_prefix
from web3 import Web3, HTTPProvider
from web3.datastructures import AttributeDict
from web3.exceptions import TransactionNotFound
from web3.types import HexBytes

from base.models import AbstractBaseModel
from backend.consts import (
    ETH_LIKE_ADDRESS_LENGTH,
    ETH_LIKE_HASH_LENGTH,
    MAX_WEI_DIGITS,
    NETWORK_ERROR,
    RPC_PROVIDER_ERROR,
    RPC_PROVIDER_INFO,
    TRANSACTION_ERROR,
    TRANSACTION_INFO,
    TRANSACTION_WARNING,
)
from networks.types import HASH_LIKE
from .exceptions import (
    CustomRpcProviderExceedListRange,
    NetworkNotFound,
    ProviderNotConnected,
)
from .services.functions import (
    convert_to_checksum_address_format,
    reset_connection,
)


# Create your models here.
class Network(AbstractBaseModel):
    title = CharField(
        max_length=255,
        verbose_name='Title',
    )
    rpc_url_list = JSONField(
        verbose_name='RPC URL List',
        default=list,
        blank=True,
    )

    class Meta:
        db_table = 'networks'
        ordering = '-_created_at',

    def __str__(self) -> str:
        return f'{self.title} (id: {self.id})'

    @property
    def rpc_provider(self):
        message = ''

        for rpc_url in self.rpc_url_list:
            info(
                RPC_PROVIDER_INFO.format(
                    f'Trying to connect to \"{self.title}\" '
                    f'node with url: \"{rpc_url}\"'
                )
            )

            provider = Web3(HTTPProvider(rpc_url))

            if provider.isConnected():
                info(
                    RPC_PROVIDER_INFO.format(
                        f'Connection to \"{rpc_url}\" was successful'
                    )
                )

                return provider

            message = (
                f'RPC provider with the URL \"{rpc_url}\" not loaded.'
            )

            exception(RPC_PROVIDER_ERROR.format(message))

        raise ProviderNotConnected(message)

    def get_rpc_provider(self, url_number):
        if url_number >= len(self.rpc_url_list):
            raise CustomRpcProviderExceedListRange(
                f"Can't connect to \"{self.title}\" network"
            )

        rpc_url = self.rpc_url_list[url_number]

        info(
            RPC_PROVIDER_INFO.format(
                f'Trying to connect to \"{self.title}\" '
                f'node with url: {rpc_url}'
            )
        )

        provider = Web3(HTTPProvider(rpc_url))

        if provider.isConnected():
            info(
                RPC_PROVIDER_INFO.format(
                    f'Connection to \"{rpc_url}\" was successful'
                )
            )

            return provider

        message = (
            f'RPC provider with the URL \"{rpc_url}\" not loaded'
        )

        exception(RPC_PROVIDER_ERROR.format(message))

        raise ProviderNotConnected(message)

    @classmethod
    def get_network(cls, network_id: UUID):
        try:
            network = cls.objects.get(
                id=network_id,
            )
        except Network.DoesNotExist as exception_error:
            message = (
                f'Network with the \"{network_id}\" id not found in database.'
                f' Error description: \"{exception_error.__str__()}\"'
            )

            exception(NETWORK_ERROR.format(message))

            raise NetworkNotFound(message)

        return network

    def get_gas_price(self, provider: Web3 = None):
        if not provider:
            return self.rpc_provider.eth.gasPrice

        return provider.eth.gasPrice


class CustomRpcProvider:
    """
    That's class wraps methods of web3 rpc provider and switches to the
    support node if connection errors happened
    """

    def __init__(self, network: Network, url_number: int = 0):
        self.network = network
        self.url_number = url_number

    @property
    def rpc_provider(self):
        rpc_provider = self.network.get_rpc_provider(self.url_number)

        return rpc_provider

    @reset_connection
    def get_current_block_number(self):
        return self.rpc_provider.eth.get_block_number()

    @reset_connection
    def get_contract(self, address: str, abi: str):
        return self.rpc_provider.eth.contract(
            address=convert_to_checksum_address_format(address),
            abi=abi,
        )

    @reset_connection
    def get_transaction(
            self,
            txn_hash: HASH_LIKE,
    ):
        return self.rpc_provider.eth.getTransaction(txn_hash)

    @reset_connection
    def get_transaction_receipt(
            self,
            txn_hash: HASH_LIKE,
    ):
        return self.rpc_provider.eth.getTransactionReceipt(txn_hash)

    @reset_connection
    def wait_for_transaction_receipt(
        self,
        txn_hash: HASH_LIKE,
        timeout: int = settings.DEFAULT_TXN_TIMEOUT,
        poll_latency: int = settings.DEFAULT_POLL_LATENCY
    ):
        return self.rpc_provider.eth.waitForTransactionReceipt(
            txn_hash,
            timeout,
            poll_latency,
        )

    @reset_connection
    def get_balance(self, address: str):
        return self.rpc_provider.eth.getBalance(
            convert_to_checksum_address_format(address)
        )

    @reset_connection
    def get_transaction_count(self, address):
        return self.rpc_provider.eth.getTransactionCount(
            convert_to_checksum_address_format(address),
            'pending'
        )

    @reset_connection
    def send_raw_transaction(self, signed_transaction):
        return self.rpc_provider.eth.sendRawTransaction(signed_transaction)

    @reset_connection
    def get_gas_price(self):
        return self.rpc_provider.eth.gasPrice

    @reset_connection
    def sign_transaction(self, transaction, private_key):
        return self.rpc_provider.eth.account.sign_transaction(
            transaction_dict=transaction,
            private_key=private_key,
        )


class Transaction(AbstractBaseModel):
    network = ForeignKey(
        to=Network,
        on_delete=PROTECT,
        related_name='network_transactions',
        verbose_name='Network',
    )
    hash = CharField(
        unique=True,
        max_length=ETH_LIKE_HASH_LENGTH,
        verbose_name='Hash',
    )
    block_hash = CharField(
        max_length=ETH_LIKE_HASH_LENGTH,
        verbose_name='Block hash',
        blank=True,
        default='',
    )
    block_number = PositiveIntegerField(
        verbose_name='Block number',
        blank=True,
        default=0,
    )
    sender = CharField(
        max_length=ETH_LIKE_ADDRESS_LENGTH,
        verbose_name='Sender (from)',
        default='',
    )
    receiver = CharField(
        max_length=ETH_LIKE_ADDRESS_LENGTH,
        verbose_name='Receiver (to)',
        default='',
    )
    gas = DecimalField(
        max_digits=MAX_WEI_DIGITS,
        decimal_places=0,
        verbose_name='Gas limit',
        default=0,
    )
    gas_price = DecimalField(
        max_digits=MAX_WEI_DIGITS,
        decimal_places=0,
        verbose_name='Gas price',
        default=0,
    )
    nonce = PositiveIntegerField(
        verbose_name='Nonce',
        default=0,
    )
    sign_r = CharField(
        max_length=ETH_LIKE_HASH_LENGTH,
        verbose_name='R',
        default='',
    )
    sign_s = CharField(
        max_length=ETH_LIKE_HASH_LENGTH,
        verbose_name='S',
        default='',
    )
    sign_v = CharField(
        max_length=ETH_LIKE_HASH_LENGTH,
        verbose_name='V',
        default='',
    )
    index = PositiveIntegerField(
        verbose_name='Index',
        blank=True,
        default=0,
    )
    type = CharField(
        max_length=255,
        verbose_name='Type',
        default='',
        blank=True,
    )
    value = DecimalField(
        max_digits=MAX_WEI_DIGITS,
        decimal_places=0,
        verbose_name='Value',
        default=0,
    )
    data = JSONField(
        verbose_name='Data',
        default=dict,
        blank=True,
    )
    event_data = JSONField(
        verbose_name='Event data',
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'transactions'
        ordering = '-_created_at',

    def __str__(self) -> str:
        return f'{self.hash} in {self.network.title} (id: {self.id})'

    def save(self, *args, **kwargs) -> None:
        self.hash = self.hash.lower()
        # self.block_hash = self.block_hash.lower()

        if self.block_number is None:
            self.block_number = 0

        if self.index is None:
            self.index = 0

        if self.block_hash is None:
            self.block_hash = ''

        self.sender = self.sender.lower()
        self.receiver = self.receiver.lower()
        self.receiver = self.receiver.lower()
        self.sign_r = self.sign_r.lower()
        self.sign_s = self.sign_s.lower()
        self.type = self.type.lower()

        return super().save(*args, **kwargs)

    def get_block_number(self) -> int:
        return self.block_number

    @classmethod
    def get_last_block_number(cls, network_id: UUID) -> int:
        transaction = cls.objects \
            .filter(
                network_id=network_id,
            ) \
            .last()

        if not transaction:
            warning(
                TRANSACTION_WARNING.format(
                    f'No transactions in the network with \"{network_id}\" id.'
                )
            )

            return

        return transaction.block_number

    @classmethod
    def get_transaction(cls, network_id: UUID, txn_hash: HASH_LIKE):
        if isinstance(txn_hash, HexBytes):
            txn_hash = txn_hash.hex()

        try:
            transaction = cls.objects.get(
                network_id=network_id,
                hash__iexact=txn_hash,
            )
        except Transaction.DoesNotExist as exception_error:
            exception(
                TRANSACTION_ERROR.format(
                    f'Transaction with the \"{txn_hash}\" hash in'
                    f' the \"{network_id}\" network not found in database.'
                    f'Error description: \"{exception_error}.\"'
                )
            )

            return

        return transaction

    @staticmethod
    def get_transaction_by_hash(
        rpc_provider: CustomRpcProvider,
        txn_hash: HASH_LIKE,
    ):
        # TODO: Добавить обработку исключения TransactionNotFound.
        try:
            transaction = rpc_provider.get_transaction(txn_hash)

            info(TRANSACTION_INFO.format(transaction))

            result = {}

            for _, item, in enumerate(transaction):
                item_value = transaction.get(item)

                if (
                    isinstance(item_value, bytes)
                    or isinstance(item_value, HexBytes)
                ):
                    item_value = add_0x_prefix(item_value.hex())

                result.update({item: item_value})

            return AttributeDict(result)
        except TransactionNotFound as exception_error:
            exception(exception_error)

        return

    @staticmethod
    def waiting_transaction_receipt(
        rpc_provider: CustomRpcProvider,
        txn_hash: HASH_LIKE,
        timeout: int = settings.DEFAULT_TXN_TIMEOUT,
        poll_latency: int = 1
    ):
        return rpc_provider.wait_for_transaction_receipt(
            txn_hash,
            timeout,
            poll_latency,
        )

    @staticmethod
    def get_transaction_receipt(
        rpc_provider: CustomRpcProvider,
        hash: HASH_LIKE,
    ):
        return rpc_provider.get_transaction_receipt(hash)

    @staticmethod
    def get_transaction_status(
        rpc_provider: CustomRpcProvider,
        txn_hash: HASH_LIKE,
    ):
        transaction = Transaction.waiting_transaction_receipt(
            rpc_provider,
            txn_hash,
        )

        return transaction.status