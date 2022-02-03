from time import time
from math import sqrt

from django.conf import settings
from base.requests import send_post_request
from best_apr.models import Pool


def tick_to_sqrtPrice(tick):
    return sqrt(pow(1.0001, tick))


def get_amounts(liquidity, tickLower, tickUpper, currentTick):
    currentPrice = tick_to_sqrtPrice(currentTick)
    lowerPrice = tick_to_sqrtPrice(tickLower)
    upperPrice = tick_to_sqrtPrice(tickUpper)
    if currentPrice < lowerPrice:
        amount1 = 0
        amount0 = liquidity * (1 / lowerPrice - 1 / upperPrice)
    elif lowerPrice <= currentPrice <= upperPrice:
        amount1 = liquidity * (currentPrice - lowerPrice)
        amount0 = liquidity * (1 / currentPrice - 1 / upperPrice)
    else:
        amount1 = liquidity * (upperPrice - lowerPrice)
        amount0 = 0
    return amount0, amount1


def get_eternal_farmings_id():
    ids_json = send_post_request(settings.SUBGRAPH_FARMING_URL, json={'query': """query {
      eternalFarmings(first: 1000,where:{isDetached:false}) {
        id
      }
    }"""})

    return ids_json['data']['eternalFarmings']


def get_positions_in_eternal_farming(farming_id):
    ids_json = send_post_request(settings.SUBGRAPH_FARMING_URL, json={'query': """query {
      deposits(where:{eternalFarming:"%s"}){
        id
      }
    }""" % farming_id})

    return ids_json['data']['deposits']


def get_positions_by_id(ids):
    ids_array = [i['id'] for i in ids]
    positions_json = send_post_request(settings.SUBGRAPH_URL, json={'query': """query {
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
          tick
        }
      }
    }""" % str(ids_array).replace("'", '"')})

    return positions_json['data']['positions']


def get_position_snapshots_from_subgraph():
    positions_json = send_post_request(settings.SUBGRAPH_URL, json={'query': """query {
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


def get_positions_from_subgraph():
    positions_json = send_post_request(settings.SUBGRAPH_URL, json={'query': """query {
    positions(first:1000){
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


def get_previous_block_number():
    previous_date = int(time()) - settings.APR_DELTA
    block_json = send_post_request(settings.SUBGRAPH_BLOCKS_URLS, json={'query': """query {
        blocks(first: 1, orderBy: timestamp, orderDirection: desc, where:{timestamp_lt:%s, timestamp_gt:%s}) {
            number
          }
    }""" % (str(previous_date), str(previous_date - settings.BLOCK_DELTA))})
    return block_json['data']['blocks'][0]['number']


def get_current_pools_info():
    pools_json_previous_raw = send_post_request(settings.SUBGRAPH_URL, json={'query': """query {
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
        }""" % get_previous_block_number()})

    pools_json_previous = {}

    for pool in pools_json_previous_raw['data']['pools']:
        pools_json_previous[pool['id']] = {'feesToken0': pool['feesToken0'], 'feesToken1': pool['feesToken1']}

    pools_json = send_post_request(settings.SUBGRAPH_URL, json={'query': """query {
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


def update_pools_apr():
    positions_json = get_positions_from_subgraph()
    pools_json = get_current_pools_info()

    pools_tick = {}
    pools_current_tvl = {}
    pools_fees = {}

    for pool in pools_json:
        pools_tick[pool['id']] = int(pool['tick'])
        pools_current_tvl[pool['id']] = 0
        try:
            pools_fees[pool['id']] += pool['feesToken0']
        except KeyError:
            pools_fees[pool['id']] = pool['feesToken0']
        pools_fees[pool['id']] += pool['feesToken1'] * float(pool['token0Price'])

    for position in positions_json:
        current_tick = pools_tick[position['pool']['id']]
        if int(position['tickLower']['tickIdx']) < current_tick < int(position['tickUpper']['tickIdx']):
            (amount0, amount1) = get_amounts(
                int(position['liquidity']),
                int(position['tickLower']['tickIdx']),
                int(position['tickUpper']['tickIdx']),
                current_tick,
            )
            amount0 = amount0 / pow(10, int(position['token0']['decimals']))
            amount1 = (amount1 / pow(10, int(position['token1']['decimals'])))
            pools_current_tvl[position['pool']['id']] += amount0
            pools_current_tvl[position['pool']['id']] += amount1 * float(position['pool']['token0Price'])

    for pool in pools_json:
        pool_object = Pool.objects.filter(address=pool['id'])
        if not pool_object:
            pool_object = Pool.objects.create(
                title=pool['token0']['name'] + ' : ' + pool['token1']['name'],
                address=pool['id'],
            )
        else:
            pool_object = pool_object[0]
        if pools_current_tvl[pool['id']]:
            pool_object.last_apr = \
                (pools_fees[pool_object.address] * 365 / pools_current_tvl[pool['id']]) * 100
        else:
            pool_object.last_apr = 0.0
        pool_object.save()


def update_eternal_farmings_tvl():
    farmings_id = get_eternal_farmings_id()
    for farming_id in farmings_id:
        token_ids = get_positions_in_eternal_farming(farming_id['id'])
        total_amount0 = 0
        total_amount1 = 0
        positions = get_positions_by_id(token_ids)
        for position in positions:
            (amount0, amount1) = get_amounts(
                int(position['liquidity']),
                int(position['tickLower']['tickIdx']),
                int(position['tickUpper']['tickIdx']),
                int(position['pool']['tick']),
            )
            total_amount0 += amount0
            total_amount1 += amount1
