"""Strategies hold 'magic numbers' related to running sim engine"""
import logging
log = logging.getLogger('simstrategy')

from enforce_typing import enforce_types # type: ignore[import]
import typing

from .parts.agents.util.constants import *
from .parts.agents.util.mathutil import Range
from .parts.agents.util.strutil import StrMixin
    
@enforce_types
class SimStrategy(StrMixin):
    
    def __init__(self):
        #seconds per time step (tick)
        self.time_step: int = 1
        
        #max # time steps (ticks) to run until
        self.max_ticks = 100000

    def setTimeStep(self, time_step: int):
        """How many seconds are there in each time step (tick)?"""
        self.time_step = time_step
        
    def setMaxTicks(self, max_ticks: int):
        """What's the max # time steps (ticks) to run until?"""
        self.max_ticks = max_ticks
        
    def setMaxTime(self, val: int, unit:str):
        """Convenience function set max_ticks according to a time unit.
        Examples:
        val = 4, unit = 'hours' --> max time is 4 hours
        val = 10, unit = 'years' --> max time is 10 years
        Units may be: ticks, hours, days, months, years
        """        
        if unit == 'ticks':
            max_ticks = val
            self.max_ticks = max_ticks
        elif unit == 'hours':
            max_hours = val
            self.max_ticks = (max_hours * S_PER_HOUR / self.time_step + 1)
        elif unit == 'days':
            max_days = val
            self.max_ticks = (max_days * S_PER_DAY / self.time_step + 1)
        elif unit == 'months':
            max_months = val
            self.max_ticks = (max_months * S_PER_MONTH / self.time_step + 1)
        elif unit == 'years':
            max_years = val
            self.max_ticks = (max_years * S_PER_YEAR / self.time_step + 1)
        else:
            raise ValueError(unit)

@enforce_types
class Schedule(StrMixin):
    def __init__(self, interval: int, n_actions: int):
        if SAFETY:
            assert interval > 0
            assert n_actions > 0
        
        self.interval: int = interval # time between actions (s)
        self.n_actions: float = n_actions
    
