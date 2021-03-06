# @date 2019-01-19
# @author Frederic SCHERMA
# @license Copyright (c) 2019 Dream Overflow
# Crystal Ball indicator strategy trader.

from strategy.timeframebasedstrategytrader import TimeframeBasedStrategyTrader
from strategy.strategyindmargintrade import StrategyIndMarginTrade
from strategy.strategysignal import StrategySignal

from instrument.instrument import Instrument

from strategy.indicator import utils
from strategy.indicator.score import Score

from common.utils import timeframe_to_str

from .cbsuba import CrystalBallStrategySubA
from .cbparameters import DEFAULT_PARAMS

import logging
logger = logging.getLogger('siis.strategy.crystalball')


class CrystalBallStrategyTrader(TimeframeBasedStrategyTrader):
    """
    Crystal Ball indicator strategy trader.
    """

    def __init__(self, strategy, instrument, params):
        super().__init__(strategy, instrument, Instrument.TF_TICK)

        # mean when there is already a position on the same direction does not increase in the same direction if 0 or increase at max N times
        self.pyramided = params['pyramided']
        self.max_trades = params['max-trades']

        self.min_price = params['min-price']
        self.min_vol24h = params['min-vol24h']

        self.min_traded_timeframe = self.timeframe_from_param(params.get('min-traded-timeframe', "15m"))
        self.max_traded_timeframe = self.timeframe_from_param(params.get('max-traded-timeframe', "4h"))

        for k, timeframe in strategy.timeframes_config.items():
            if timeframe['mode'] == 'A':
                sub = CrystalBallStrategySubA(self, timeframe)
                self.timeframes[timeframe['timeframe']] = sub
            else:
                continue

        self._last_filter_cache = (0, False, False)

        self.setup_streaming()

    def filter_market(self, timestamp):
        """
        The first boolean mean accept, the second compute.
        Return True, True if the market is accepted and can be computed this time.
        """
        if timestamp - self._last_filter_cache[0] < 60*60:  # only once per hour
            return self._last_filter_cache[1], self._last_filter_cache[2]

        # if there is no actives trades we can avoid computation on some ininteresting markets
        if self.trades:
            if self.instrument.vol24h_quote is not None and self.instrument.vol24h_quote < self.min_vol24h:
                # accepted but 24h volume is very small (rare possibilities of exit)
                self._last_filter_cache = (timestamp, True, False)
                return True, False

        self._last_filter_cache = (timestamp, True, True)
        return True, True

    def process(self, timestamp):
        # update data at tick level
        self.gen_candles_from_ticks(timestamp)

        accept, compute = self.filter_market(timestamp)
        if not accept:
            return

        # and compute
        entries = []
        exits = []

        if compute:
            entries, exits = self.compute(timestamp)

        trader = self.strategy.trader()

        if not trader:
            self._last_filter_cache = (timestamp, False, False)
            return False, False

        for entry in entries:
            self.notify_signal(timestamp, entry)

        for exit in exits:
            self.notify_signal(timestamp, exit)

        # update user managed actives trades
        self.update_trades(timestamp)
