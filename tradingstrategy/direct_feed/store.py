"""Cached data store for trade feeds.

We store

- Block headers

- Fetched trades

We do not store

- Candles (always regenerated)
"""
from pathlib import Path

from eth_defi.event_reader.parquet_block_data_store import ParquetDatasetBlockDataStore
from tradingstrategy.direct_feed.trade_feed import TradeFeed


def save_trade_feed(trade_feed: TradeFeed, base_path: Path, partition_size: int):
    """Save the trade and block header data.

    :param trade_feed:
        Save trades and block headers from this feed.

    :param base_path:
        Base folder where data is dumped.
        Both headers and trades get their own Parquet datasets
        as folders.

    :parma partition_size:
        Partition size for the store.

    :return:
    """
    header_store = ParquetDatasetBlockDataStore(Path(base_path), partition_size)
    trade_store = ParquetDatasetBlockDataStore(Path(base_path), partition_size)

    # Save headers
    headers_df = trade_feed.reorg_mon.to_pandas(partition_size)
    header_store.save(headers_df)

    # Save trades
    trades_df = trade_feed.to_pandas(partition_size)
    trade_store.save(trades_df)

    assert not header_store.is_virgin(), f"Headers not correctly written"
    assert not trade_store.is_virgin(), f"Trades not correctly written"


def load_trade_feed(trade_feed: TradeFeed, base_path: Path, partition_size: int) -> bool:
    """Load trade and block header data.

    :param trade_feed:
        Save trades and block headers from this feed.

    :param base_path:
        Base folder where data is dumped.
        Both headers and trades get their own Parquet datasets
        as folders.

    :parma partition_size:
        Partition size for the store.

    :return:
        True if any data was loaded.

    """
    header_store = ParquetDatasetBlockDataStore(Path(base_path).joinpath("blocks"), partition_size)
    trade_store = ParquetDatasetBlockDataStore(Path(base_path).joinpath("trades"), partition_size)

    if header_store.is_virgin():
        return False

    assert not trade_store.is_virgin(), f"Store {base_path} not in use / incorrectly written"

    headers_df_2 = header_store.load()
    trades_df_2 = trade_store.load()

    trade_feed.reorg_mon.restore(headers_df_2)
    trade_feed.restore(trades_df_2)

    return True
