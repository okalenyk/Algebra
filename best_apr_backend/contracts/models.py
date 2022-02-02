from logging import exception
# from typing import Union
from uuid import UUID

# from django.conf import settings
from django.db.models import (
    CharField,
    # DecimalField,
    ForeignKey,
    # PositiveIntegerField,
    PROTECT,
    JSONField,
)
# from django.utils.functional import cached_property
from eth_utils import add_0x_prefix
from web3 import Web3
# from web3.datastructures import AttributeDict
# from web3.types import HexBytes, Wei
from web3.types import HexBytes, TxParams

from base.models import AbstractBaseModel
from backend.consts import (
    DEFAULT_CRYPTO_ADDRESS,
    CONTRACT_ERROR,
    ETH_LIKE_ADDRESS_LENGTH,
    # ETH_LIKE_HASH_LENGTH,
    # MAX_WEI_DIGITS,
)
from networks.models import Network, CustomRpcProvider
# from networks.models import Network, Transaction, CustomRpcProvider
# from networks.services.functions import convert_to_checksum_address_format
# from networks.types import HASH_LIKE
from .exceptions import (
    ContractMultipleObjectsReturned,
    ContractNotFound,
)


class BaseContract(AbstractBaseModel):
    title = CharField(
        max_length=255,
        verbose_name='Title',
        blank=True,
    )
    address = CharField(
        max_length=ETH_LIKE_ADDRESS_LENGTH,
        verbose_name='Address',
        default=DEFAULT_CRYPTO_ADDRESS,
    )
    abi = JSONField(
        verbose_name='ABI',
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        if not self.title:
            return (
                f'Contract at {self.address} in {self.network.title}'
                f' (id: {self.id})'
            )
        return (
            f'{self.title} at {self.address} in {self.network.title}'
            f' (id: {self.id})'
        )

    def save(self, *args, **kwargs) -> None:
        self.address = self.address.lower()

        return super().save(*args, **kwargs)

    def load_contract(
            self,
            provider: CustomRpcProvider = None,
            address: str = None,
    ):
        if not provider:
            provider = CustomRpcProvider(self.network)
        if not address:
            address = self.address

        # return provider.eth.contract(
        #     address=provider.toChecksumAddress(address),
        #     abi=self.abi,
        # )

        return provider.get_contract(
            address=address,
            abi=self.abi,
        )

    def decode_function_input(
            self,
            txn_data_input: dict,
            provider: Web3 = None
    ):
        if not provider:
            provider = Web3(self.network)

        txn_data_decoded_input = self \
            .load_contract(provider) \
            .decode_function_input(txn_data_input)[-1]

        for _, item, in enumerate(txn_data_decoded_input):
            item_value = txn_data_decoded_input.get(item)

            # TODO: Нужно изменить параметры транзакции на изменение статуса
            #  в целевой сети с dict на tuple.
            if isinstance(item_value, tuple):
                result = tuple(
                    add_0x_prefix(tuple_item.hex())
                    if isinstance(tuple_item, (bytes, HexBytes))
                    else tuple_item
                    for tuple_item in item_value
                )

                txn_data_decoded_input.update({item: result})
            ###

            if isinstance(item_value, (bytes, HexBytes)):
                item_value = add_0x_prefix(item_value.hex())
                txn_data_decoded_input.update({item: item_value})

        return txn_data_decoded_input

    @classmethod
    def get_contract(cls, contract_id: UUID):
        try:
            contract = cls.objects.get(
                id=contract_id,
            )
        except cls.DoesNotExist:
            message = (
                f'Contract with the \"{contract_id}\" id '
                f'not found in database.'
            )

            exception(CONTRACT_ERROR.format(message))

            raise ContractNotFound(message)
        except cls.MultipleObjectsReturned:
            message = (
                f'Several objects of contracts have been received'
                f' with the \"{contract_id}\" id from database.'
            )

            exception(CONTRACT_ERROR.format(message))

            raise ContractMultipleObjectsReturned(message)

        return contract

    @classmethod
    def get_contract_by_address(cls, network_id: UUID, address: str):
        try:
            contract = Contract.objects.get(
                network_id=network_id,
                address__iexact=address,
            )
        except Contract.DoesNotExist:
            message = (
                f'Contract with the \"{address}\" address in'
                f' the \"{network_id}\" network not found in database.'
            )

            exception(CONTRACT_ERROR.format(message))

            raise ContractNotFound(message)
        except Contract.MultipleObjectsReturned:
            message = (
                f'Several objects of contracts have been received'
                f' with the \"{address}\" address in the \"{network_id}\"'
                ' network from database.'
            )

            exception(CONTRACT_ERROR.format(message))

            raise ContractMultipleObjectsReturned(message)

        return contract


# Create your models here.
class Contract(BaseContract):
    network = ForeignKey(
        to=Network,
        on_delete=PROTECT,
        related_name='network_contracts',
        verbose_name='Network',
    )

    class Meta:
        db_table = 'contracts'
        ordering = '-_created_at',


class TokenContract(BaseContract):
    network = ForeignKey(
        to=Network,
        on_delete=PROTECT,
        related_name='network_token_contracts',
        verbose_name='Network',
        blank=True,
        null=True,
    )

    class Meta:
        db_table = 'token_contracts'
        ordering = '-_created_at',

    def __str__(self) -> str:
        if not self.title and not self.network:
            return (
                f'Contract at {self.address} (id: {self.id})'
            )
        elif self.title and not self.network:
            return (
                f'{self.title} at {self.address}'
                f' (id: {self.id})'
            )
        return (
            f'{self.title} at {self.address} in {self.network.title}'
            f' (id: {self.id})'
        )
