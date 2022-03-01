from logging import exception, warning, info
from uuid import UUID
from time import time

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
from base.requests import send_post_request
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
from networks.types import HASH_LIKE, ADDRESS_LIKE
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
    subgraph_url = URLField(
        help_text='Subgraph about main contracts'
    )
    subgraph_blocks_urls = URLField(
        help_text='Subgraph about blockchain'
    )
    subgraph_farming_url = URLField(
        help_text='Subgraph about farmings'
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

    def get_token_info_by_address(self, address):
        ids_json = send_post_request(self.subgraph_url, json={'query': """query {
          tokens(where:{id:"%s"}){
            derivedMatic
            decimals
          }
        }""" % address})

        return ids_json['data']['tokens']

    def get_eternal_farmings_info(self, ):
        ids_json = send_post_request(self.subgraph_farming_url, json={'query': """query {
          eternalFarmings{
            id
            rewardToken
            bonusRewardToken
            rewardRate
            bonusRewardRate
          }
        }"""})

        return ids_json['data']['eternalFarmings']

    def get_positions_in_eternal_farming(self, farming_id):
        ids_json = send_post_request(self.subgraph_farming_url, json={'query': """query {
          deposits(where:{eternalFarming:"%s"}){
            id
          }
        }""" % farming_id})

        return ids_json['data']['deposits']

    def get_positions_by_id(self, ids):
        ids_array = [i['id'] for i in ids]
        positions_json = send_post_request(self.subgraph_url, json={'query': """query {
          positions(where:{id_in:%s}){
            id
            liquidity
            tickLower{
              tickIdx
            }
            tickUpper{
              tickIdx
            }
            pool{
              token0{
                name
                decimals
                derivedMatic
              }
              token1{
                name
                decimals
                derivedMatic
              }
              tick
            }
          }
        }""" % str(ids_array).replace("'", '"')})

        return positions_json['data']['positions']

    def get_position_snapshots_from_subgraph(self, ):
        positions_json = send_post_request(self.subgraph_url, json={'query': """query {
      positionSnapshots{
        liquidity,
        feeGrowthInside0LastX128,
        feeGrowthInside1LastX128,
        position{
          id
          tickLower{
            tickIdx
          }
          tickUpper{
            tickIdx
          }
        }
      }
    }"""})
        return positions_json['data']['positionSnapshots']

    def get_positions_from_subgraph(self, ):
        positions_json = send_post_request(self.subgraph_url, json={'query': """query {
            positions(first:1000, where:{liquidity_gt:0}){
            tickLower{
                tickIdx
            }
            tickUpper{
                tickIdx
            }
            liquidity
            depositedToken0
            depositedToken1
            token0{
              decimals
            }
            token1{
              decimals
            }
            pool{
              id
              token0Price
            }
          }
        }"""})
        return positions_json['data']['positions']

    def get_previous_block_number(self):
        previous_date = int(time()) - settings.APR_DELTA
        block_json = send_post_request(self.subgraph_blocks_urls, json={'query': """query {
            blocks(first: 1, orderBy: timestamp, orderDirection: desc, where:{timestamp_lt:%s, timestamp_gt:%s}) {
                number
              }
        }""" % (str(previous_date), str(previous_date - settings.BLOCK_DELTA))})
        print((str(previous_date), str(previous_date - settings.BLOCK_DELTA)))
        return block_json['data']['blocks'][0]['number']

    def get_current_pools_info(self):
        pools_json_previous_raw = send_post_request(self.subgraph_url, json={'query': """query {
        pools(block:{number:%s},first: 1000, orderBy: id){
            feesToken0
            feesToken1
            id
            token0{
            name
            }
            token1{
            name
            }
            token0Price
            tick
         }
            }""" % self.get_previous_block_number()})

        pools_json_previous = {}

        for pool in pools_json_previous_raw['data']['pools']:
            pools_json_previous[pool['id']] = {'feesToken0': pool['feesToken0'], 'feesToken1': pool['feesToken1']}

        pools_json = send_post_request(self.subgraph_url, json={'query': """query {
        pools(first: 1000, orderBy: id){
            feesToken0
            feesToken1
            id
            token0{
            name
            }
            token1{
            name
            }
            token0Price
            tick
         }
            }"""})

        pools_json = pools_json['data']['pools']

        for i in range(len(pools_json)):
            try:
                pools_json[i]['feesToken0'] = \
                    float(pools_json[i]['feesToken0']) - float(pools_json_previous[pools_json[i]['id']]['feesToken0'])
                pools_json[i]['feesToken1'] = \
                    float(pools_json[i]['feesToken1']) - float(pools_json_previous[pools_json[i]['id']]['feesToken1'])
            except KeyError:
                pools_json[i]['feesToken0'] = float(pools_json[i]['feesToken0'])
                pools_json[i]['feesToken1'] = float(pools_json[i]['feesToken1'])

        return pools_json


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
    def get_balance(self, address: ADDRESS_LIKE):
        return self.rpc_provider.eth.getBalance(
            convert_to_checksum_address_format(address)
        )

    @reset_connection
    def get_transaction_count(self, address: ADDRESS_LIKE):
        return self.rpc_provider.eth.getTransactionCount(
            convert_to_checksum_address_format(address),
            'pending'
        )

    @reset_connection
    def send_raw_transaction(self, signed_transaction):
        return self.rpc_provider.eth.sendRawTransaction(signed_transaction)

    @reset_connection
    def get_logs(self, contract, event_name, from_block, to_block):
        web3_contract_instance = contract.load_contract(
            provider=self,
        )

        event = getattr(
            web3_contract_instance.events,
            event_name,
        )

        return event().getLogs(
            fromBlock=from_block,
            toBlock=to_block,
        )

    @reset_connection
    def contract_function_call(
        self,
        contract,
        contract_function_name: str,
        params: tuple,
        contract_address: str = None,
    ):
        if not contract_address:
            contract_address = contract.address

        contract_function = contract.load_contract(
            address=contract_address,
            provider=self,
        ).get_function_by_name(contract_function_name)(
            *params
        )

        return contract_function.call()


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
