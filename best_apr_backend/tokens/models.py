from logging import exception, warning
from typing import Union
from uuid import UUID

from django.conf import settings
from django.db.models import (
    PROTECT,
    BooleanField,
    CharField,
    FloatField,
    ForeignKey,
    PositiveIntegerField,
)
from django.db.models.fields import DecimalField, FloatField, IntegerField
from django.db.utils import IntegrityError
from eth_typing import ChecksumAddress

from base.models import AbstractBaseModel
from contracts.models import TokenContract
from backend.consts import (
    DEFAULT_CRYPTO_ADDRESS,
    DEFAULT_TOKEN_DECIMALS,
    TOKEN_ERROR,
    ETH_LIKE_ADDRESS_LENGTH,
)
from networks.models import Network
from networks.services.functions import convert_to_checksum_address_format
from .exceptions import (
    TokenMultipleObjectsReturned,
    TokenNotCreated,
)


# Create your models here.
class Token(AbstractBaseModel):
    name = CharField(
        max_length=512,
        verbose_name='Name',
    )
    symbol = CharField(
        max_length=255,
        verbose_name='Symbol',
    )
    address = CharField(
        max_length=ETH_LIKE_ADDRESS_LENGTH,
        verbose_name='Address',
    )
    decimals = PositiveIntegerField(
        verbose_name='Decimals',
        default=DEFAULT_TOKEN_DECIMALS,
    )
    network = ForeignKey(
        to=Network,
        on_delete=PROTECT,
        related_name='network_tokens',
        verbose_name='Network',
    )
    is_deflation = BooleanField(
        default=False,
        verbose_name='Is deflation',
    )
    slippage = FloatField(
        default=settings.DEFAULT_SLIPPAGE,
        verbose_name='Slippage',
    )

    class Meta:
        db_table = 'tokens'
        ordering = '-_created_at',

    def __str__(self) -> str:
        return f'{self.symbol} at {self.address} (id: {self.id})'

    def save(self, *args, **kwargs) -> None:
        self.name = self.name.lower()
        self.symbol = self.symbol.lower()
        self.address = self.address.lower()

        return super().save(*args, **kwargs)

    @classmethod
    def add_token(cls, network_id: UUID, address: Union[str, ChecksumAddress]):
        network = Network.get_network(network_id)
        # TODO: Загружать общий для токенов контракт.
        token_contract = TokenContract \
            .get_contract_by_address(network_id, DEFAULT_CRYPTO_ADDRESS) \
            .load_contract(address=convert_to_checksum_address_format(address))

        try:
            token_name = token_contract \
                .get_function_by_name('name')().call()
            token_symbol = token_contract \
                .get_function_by_name('symbol')().call()
            token_decimals = token_contract \
                .get_function_by_name('decimals')().call()

            token = cls(
                network=network,
                name=token_name,
                address=address,
                symbol=token_symbol,
                decimals=token_decimals,
            )

            token.save()
        except ValueError as exception_error:
            message = (
                f'Token with the \"{address}\" address in'
                f' the \"{network.title}\" network not created.'
                f' Error description: \"{exception_error.__str__()}.\"'
            )

            exception(TOKEN_ERROR.format(message))

            raise TokenNotCreated(message)
        except IntegrityError as exception_error:
            message = (
                f'Token with the \"{address}\" address in'
                f' the \"{network.title}\" network not created.'
                f' Error description: \"{exception_error}.\"'
            )

            exception(TOKEN_ERROR.format(message))

            raise TokenNotCreated(message)
        except Exception as exception_error:
            message = (
                f'Token with the \"{address}\" address in'
                f' the \"{network.title}\" network not created.'
                f' Error description: \"{exception_error.__str__()}.\"'
            )

            exception(message)

            raise TokenNotCreated(message)

        return token

    @classmethod
    def get_token(
            cls,
            network_id: UUID,
            address: str,
    ):
        token = cls.objects.filter(
            network__id=network_id,
            address__iexact=address,
        ).first()

        if not token:
            network = Network.get_network(network_id)
            message = (
                f'Token with the \"{address}\" address in'
                f' the \"{network.title}\" network not found in database.'
            )

            warning(TOKEN_ERROR.format(message))

            token = cls.add_token(network_id, address)

        return token
