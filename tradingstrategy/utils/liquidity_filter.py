"""Filtering Uniswap trading pairs for liquidity.

- Used to build a trading pair universe with tradeable pairs of enough liquidity, no survivorship bias

- See :py:func:`build_liquidity_summary` for usage

"""
from collections import Counter
from typing import Collection

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from tradingstrategy.types import USDollarAmount, PrimaryKey
from tradingstrategy.utils.time import floor_pandas_week


def get_somewhat_realistic_max_liquidity(
    liquidity_df,
    pair_id,
    samples=10,
    broken_liquidity=100_000_000,
) -> float:
    """Get the max liquidity of a trading pair over its history.

    - Get the token by its maximum ever liquidity, so we avoid survivorship bias

    - Instead of picking the absolute top, we pick n top samples
      and choose lowest of those

    - This allows us to avoid data sampling issues when the liquidity value,
      as calculated with the function of price, might have been weird when the token launched

    :param broken_liquidity:
        Cannot have more than 100M USD

    """

    try:
        liquidity_samples = liquidity_df.obj.loc[pair_id]["close"]
        sample = min(liquidity_samples)
        if sample > broken_liquidity:
            # Filter out bad data
            return 0
        return sample
    except KeyError:
        # Pair not available, because liquidity data is not there, or zero, or broken
        return 0


def get_liquidity_today(
    liquidity_df,
    pair_id,
    delay=pd.Timedelta(days=21)
) -> float:
    """Get the current liquidity of a trading pair

    :param delay:
        Look back X days.

        To avoid indexer delays.

    :return:
        US dollars
    """

    try:
        timestamp = floor_pandas_week(pd.Timestamp.now() - delay)
        sample = liquidity_df.obj.loc[pair_id]["close"][timestamp]
        return sample
    except KeyError:
        # Pair not available, because liquidity data is not there, or zero, or broken
        return 0


def build_liquidity_summary(
    liquidity_df: pd.DataFrame | DataFrameGroupBy,
    pair_ids: Collection[PrimaryKey] | pd.Series,
    delay=pd.Timedelta(days=21)
) -> tuple[Counter[PrimaryKey, USDollarAmount], Counter[PrimaryKey, USDollarAmount]]:
    """Build a liquidity status of the trading pairs

    - Get the historical max liquidity of a pair, so we can use this for filtering without survivorship bias

    - Get the most recent liquidity (w/delay of few days)

    :param liquidity_df:
        Liquidity data. **MUST BE forward filled for no gaps and timestamp indexed.**

        Must be daily timeframe to include TVL data.

    :param pair_ids:
        Pairs we are interested in

    :param delay:
        The time lag to check the "current" today's liquidity.

        Ensure the data is indexed by the time we run this code.

    :return:
        Two counters of historical max liquidity, liquidity today
    """

    if not isinstance(liquidity_df, DataFrameGroupBy):
        liquidity_df = liquidity_df.set_index("timestamp").groupby("pair_id")

    # Get top liquidity for all of our pairs
    pair_liquidity_max_historical = Counter()
    pair_liquidity_today = Counter()
    for pair_id in pair_ids:
        pair_liquidity_max_historical[pair_id] = get_somewhat_realistic_max_liquidity(liquidity_df, pair_id)
        pair_liquidity_today[pair_id] = get_liquidity_today(liquidity_df, pair_id, delay=delay)
    return pair_liquidity_max_historical, pair_liquidity_today
