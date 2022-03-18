from math import sqrt

from datetime import datetime
from networks.models import Network
from best_apr.models import Pool, EternalFarming, LimitFarming


def tick_to_sqrt_price(tick):
    return sqrt(pow(1.0001, tick))


def get_amounts(liquidity, tickLower, tickUpper, currentTick):
    currentPrice = tick_to_sqrt_price(currentTick)
    lowerPrice = tick_to_sqrt_price(tickLower)
    upperPrice = tick_to_sqrt_price(tickUpper)
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


def update_pools_apr(network: Network):
    positions_json = network.get_positions_from_subgraph()
    pools_json = network.get_current_pools_info()

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
                network=network
            )
        else:
            pool_object = pool_object[0]
        if pools_current_tvl[pool['id']]:
            pool_object.last_apr = \
                (pools_fees[pool_object.address] * 365 / pools_current_tvl[pool['id']]) * 100
        else:
            pool_object.last_apr = 0.0
        pool_object.save()


def update_eternal_farmings_apr(network: Network):
    farmings = network.get_eternal_farmings_info()
    for farming in farmings:
        token_ids = network.get_positions_in_eternal_farming(farming['id'])
        token0 = network.get_token_info_by_address(farming['rewardToken'])[0]
        token1 = network.get_token_info_by_address(farming['bonusRewardToken'])[0]
        total_matic_amount = 0.0
        positions = network.get_positions_by_id(token_ids)
        for position in positions:
            (amount0, amount1) = get_amounts(
                int(position['liquidity']),
                int(position['tickLower']['tickIdx']),
                int(position['tickUpper']['tickIdx']),
                int(position['pool']['tick']),
            )
            total_matic_amount += amount0 * \
                                  float(position['pool']['token0']['derivedMatic']) \
                                  / 10 ** int(position['pool']['token0']['decimals'])
            total_matic_amount += amount1 \
                                  * float(position['pool']['token1']['derivedMatic']) \
                                  / 10 ** int(position['pool']['token1']['decimals'])
        reward0_per_second = int(farming['rewardRate']) * float(token0['derivedMatic']) / 10 ** int(token0['decimals'])
        reward1_per_second = int(farming['bonusRewardRate']) * float(token1['derivedMatic']) / 10 ** int(
            token1['decimals'])
        apr = (reward0_per_second + reward1_per_second) \
              / total_matic_amount * 60 * 60 * 24 * 365 * 100 if total_matic_amount > 0 else \
            -1.0

        farming_object = EternalFarming.objects.filter(hash=farming['id'])
        if not farming_object:
            farming_object = EternalFarming.objects.create(
                hash=farming['id'],
                network=network
            )
        else:
            farming_object = farming_object[0]
        farming_object.last_apr = apr
        farming_object.matic_amount = total_matic_amount
        farming_object.save()


def update_limit_farmings_apr(network: Network):
    farmings = network.get_limit_farmings_info()
    for farming in farmings:
        token_ids = network.get_positions_in_limit_farming(farming['id'])
        token0 = network.get_token_info_by_address(farming['rewardToken'])[0]
        token1 = network.get_token_info_by_address(farming['bonusRewardToken'])[0]
        total_matic_amount = 0.0
        positions = network.get_positions_by_id(token_ids)
        for position in positions:
            (amount0, amount1) = get_amounts(
                int(position['liquidity']),
                int(position['tickLower']['tickIdx']),
                int(position['tickUpper']['tickIdx']),
                int(position['pool']['tick']),
            )
            total_matic_amount += amount0 * \
                                  float(position['pool']['token0']['derivedMatic']) \
                                  / 10 ** int(position['pool']['token0']['decimals'])
            total_matic_amount += amount1 \
                                  * float(position['pool']['token1']['derivedMatic']) \
                                  / 10 ** int(position['pool']['token1']['decimals'])

        duration = 86400 * 365 / (int(farming['endTime']) - int(farming['startTime']))
        rewards_amount_0 = int(farming['reward']) * float(token0['derivedMatic']) / \
                           10 ** int(token0['decimals'])
        rewards_amount_1 = int(farming['bonusReward']) * float(token1['derivedMatic']) / \
                           10 ** int(token1['decimals'])

        apr = (rewards_amount_0 + rewards_amount_1) * duration / total_matic_amount * 100 \
            if total_matic_amount > 0 and int(farming['endTime']) > int(datetime.now().timestamp()) else -1

        farming_object = LimitFarming.objects.filter(hash=farming['id'])
        if not farming_object:
            farming_object = LimitFarming.objects.create(
                hash=farming['id'],
                network=network
            )
        else:
            farming_object = farming_object[0]
        farming_object.matic_amount = total_matic_amount
        farming_object.last_apr = apr
        farming_object.save()
