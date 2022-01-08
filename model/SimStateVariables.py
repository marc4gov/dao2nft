import logging
log = logging.getLogger('simstate')

from enforce_typing import enforce_types # type: ignore[import]
from typing import Set

from .parts.agents.util import mathutil, valuation
from .parts.agents.util.mathutil import Range
from .parts.agents.util.constants import *


@enforce_types
class SimStateVariables(object):

    def __init__(self):
        log.debug("init:begin")

        self.health = 0.0
        self.dao_members = 10
        self.OCEAN_holders = 10
        self.round_projects = 0
        self.round = 0
        self.round_volume: float = 0.0
        self.round_project_members = 10

        log.debug("init: end")

