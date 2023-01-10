from time import time

from django.conf import settings
from django.db.models import (
    CharField,
    URLField,
    JSONField
)

from base.models import AbstractBaseModel
from base.requests import send_post_request


# Create your models here.
class Network(AbstractBaseModel):
    title = CharField(
        max_length=255,
        verbose_name='Title',
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

    def get_limit_farmings_info(self, ):
        ids_json = send_post_request(self.subgraph_farming_url, json={'query': """query {
          limitFarmings{
            id
            rewardToken
            bonusRewardToken
            reward
            bonusReward
            startTime
            endTime
          }
        }"""})

        return ids_json['data']['limitFarmings']

    def get_positions_in_eternal_farming(self, farming_id):
        result = []
        i = 0

        while True:
            ids_json = send_post_request(self.subgraph_farming_url, json={'query': """query {
              deposits(where:{eternalFarming:"%s"}, first:1000, skip:%s){
                id
              }
            }""" % (farming_id, str(i*1000))})

            result += ids_json['data']['deposits']

            if len(ids_json['data']['deposits']) < 1000:
                break

        return result

    def get_positions_in_limit_farming(self, farming_id):
        result = []
        i = 0

        while True:
            ids_json = send_post_request(self.subgraph_farming_url, json={'query': """query {
              deposits(where:{incentive:"%s"}, first:1000, skip:%s){
                id
              }
            }""" % farming_id})

            result += ids_json['data']['deposits']

            if ids_json['data']['deposits'] < 1000:
                break

        return result

    def get_positions_by_id(self, ids):
        ids_array = [i['id'] for i in ids]

        result = []
        i = 0

        while True:
            positions_json = send_post_request(self.subgraph_url, json={'query': """query {
              positions(where:{id_in:%s}, first:1000, skip:%s){
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
            }""" % (str(ids_array).replace("'", '"'), str(i*1000))})

            result += positions_json['data']['positions']

            if len(positions_json['data']['positions']) < 1000:
                break

        return result

    # def get_position_snapshots_from_subgraph(self, ):
    #     positions_json = send_post_request(self.subgraph_url, json={'query': """query {
    #   positionSnapshots{
    #     liquidity,
    #     feeGrowthInside0LastX128,
    #     feeGrowthInside1LastX128,
    #     position{
    #       id
    #       tickLower{
    #         tickIdx
    #       }
    #       tickUpper{
    #         tickIdx
    #       }
    #     }
    #   }
    # }"""})
    #     return positions_json['data']['positionSnapshots']

    def get_positions_of_pool(self, pool):
        result = []
        i = 0

        while True:
            positions_json = send_post_request(self.subgraph_url, json={'query': """query {
                positions(first:1000, skip:%s, where:{liquidity_gt:0, pool:"%s"}){
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
            }""" % (str(i*1000), pool)})

            result += positions_json['data']['positions']

            if len(positions_json['data']['positions']) < 1000:
                break

        return result

    def get_previous_block_number(self):
        previous_date = int(time()) - settings.APR_DELTA
        block_json = send_post_request(self.subgraph_blocks_urls, json={'query': """query {
            blocks(first: 1, orderBy: timestamp, orderDirection: desc, where:{timestamp_lt:%s, timestamp_gt:%s}) {
                number
              }
        }""" % (str(previous_date), str(previous_date - settings.BLOCK_DELTA))})
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
