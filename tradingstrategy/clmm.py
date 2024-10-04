"""Uniswap V3 CLMM data format for liquidity provision backtesting.

- `Read more about Concentrated Liquidity Market Making <https://tradingstrategy.ai/glossary/clmm>`__
"""
from dataclasses import dataclass

import pyarrow as pa


@dataclass
class CLMM:
    """Define a single CLMM candle.

    - To be used with `Dementer backtesting framework <https://github.com/zelos-alpha/demeter/tree/master/demeter>`__ but will work with others

    TODO: Document columns.
    """

    def get_pyarrow_schema(cls) -> pa.Schema:
        # This schema is based on the original example files in Demeter repo
        schema = pa.schema([
            ("pair_id", pa.int32()),
            ("bucket", pa.timestamp("s")),
            ("open_tick", pa.uint32()),
            ("close_tick", pa.uint32()),
            ("high_tick", pa.uint32()),
            ("low_tick", pa.uint32()),
            ("current_liquidity", pa.decimal256(76)),
            ("net_amount0", pa.decimal256(76)),
            ("net_amount1", pa.decimal256(76)),
            ("in_amount0", pa.decimal256(76)),
            ("in_amount1", pa.decimal256(76)),
        ])
        return schema

