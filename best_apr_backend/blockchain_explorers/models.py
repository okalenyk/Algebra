from logging import exception
from requests.exceptions import RequestException
from uuid import UUID

from django.db.models import (
    BigIntegerField,
    CharField,
    CASCADE,
    ForeignKey,
    JSONField,
    URLField,
)

from backend.consts import ETH_LIKE_ADDRESS_LENGTH
from base.models import AbstractBaseModel
from base.requests import send_get_request
from networks.models import Network
from .exceptions import (
    EmptyRequestToEtherscanLikeAPIResult,
    RequestToEtherscanLikeAPINotCreated,
)


# Create your models here.
class EtherscanLikeBlockchainExplorer(AbstractBaseModel):
    title = CharField(
        verbose_name='Title',
        max_length=255,
    )
    network = ForeignKey(
        to=Network,
        on_delete=CASCADE,
        verbose_name='Network',
    )
    url_endpoint = URLField(
        verbose_name='URL endpoint',
    )
    api_key = CharField(
        verbose_name='API key',
        max_length=255,
    )

    class Meta:
        db_table = 'eth_like_blockchain_explorers'
        ordering = '-_created_at',
        verbose_name = 'Etherscan-like blockchain explorer'
        verbose_name_plural = 'Etherscan-like blockchain explorers'

    def __str__(self) -> str:
        return f'{self.title.upper()} (id: {self.id})'

    def get_token_transfer_data_by_address_url(
        self,
        address: str,
        start_block: int,
        end_block: int,
        asc_sort: bool = True,
    ):
        return (
            f'{self.url_endpoint}/api?module=account&action=tokentx&'
            f'address={address}&startblock={start_block}&'
            f'endblock={end_block}&sort={"desc" if not asc_sort else "asc"}&'
            f'apikey={self.api_key}'
        )


class RequestToEtherscanLikeAPI(AbstractBaseModel):
    blockchain_explorer = ForeignKey(
        to=EtherscanLikeBlockchainExplorer,
        on_delete=CASCADE,
        verbose_name='Blockchain explorer',
    )
    address = CharField(
        verbose_name='Address',
        max_length=ETH_LIKE_ADDRESS_LENGTH,
    )
    from_block = BigIntegerField(
        verbose_name='From block',
    )
    to_block = BigIntegerField(
        verbose_name='Fo block',
    )
    response = JSONField(
        verbose_name='Response',
    )

    class Meta:
        db_table = 'requests_to_eth_like_blockchain_explorers_api'
        ordering = '-_created_at',
        verbose_name = 'Request to Etherscan-like API'
        verbose_name_plural = 'Requests to Etherscan-like API'

    def __str__(self) -> str:
        return (
            f'Response from {self.blockchain_explorer.title} by '
            f'{self.address} ({self.from_block} - {self.to_block})'
        )

    @classmethod
    def get_last_response(cls, blockchain_name: str, address: str):
        try:
            return cls.objects \
                .filter(
                    blockchain_explorer__network__title__iexact=blockchain_name,
                    address__iexact=address,
                ) \
                .latest('_created_at')
        except cls.DoesNotExist:
            return

    @classmethod
    def create(
        cls,
        blockchain_explorer_id: UUID,
        address: str,
        from_block: int,
        to_block: int,
        asc_sort: bool = True,
    ):
        try:
            blockchain_explorer = EtherscanLikeBlockchainExplorer.objects.get(
                id=blockchain_explorer_id,
            )
            response = send_get_request(
                url=blockchain_explorer.get_token_transfer_data_by_address_url(
                    address=address,
                    start_block=from_block,
                    end_block=to_block,
                    asc_sort=asc_sort,
                ),
            )

            if response.get('status') == "0" and not response.get('result'):
                raise EmptyRequestToEtherscanLikeAPIResult(
                    'EmptyRequestToEtherscanLikeAPIResult'
                )

            new_response_from_etherscan_like_api = cls.objects.get_or_create(
                blockchain_explorer=blockchain_explorer,
                address=address,
                from_block=from_block,
                to_block=to_block,
                response=response,
            )

            return new_response_from_etherscan_like_api
        except EtherscanLikeBlockchainExplorer.DoesNotExist as exception_error:
            raise RequestToEtherscanLikeAPINotCreated(
                'EtherscanLikeBlockchainExplorer.DoesNotExist'
            ) from exception_error
        except EtherscanLikeBlockchainExplorer.MultipleObjectsReturned as exception_error:
            raise RequestToEtherscanLikeAPINotCreated(
                'EtherscanLikeBlockchainExplorer.MultipleObjectsReturned'
            ) from exception_error
        except RequestException as exception_error:
            raise RequestToEtherscanLikeAPINotCreated(
                'RequestException'
            ) from exception_error
        except EmptyRequestToEtherscanLikeAPIResult as exception_error:
            exception(exception_error)
            return None, None
