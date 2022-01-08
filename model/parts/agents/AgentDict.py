from enforce_typing import enforce_types # type: ignore[import]

@enforce_types
class AgentDict(dict):
    """Dict of Agent"""
    def __init__(self,*arg,**kw):
        """
        Extend the dict object to get the best of both worlds (object/dict)
        """
        super(AgentDict, self).__init__(*arg, **kw)
    
