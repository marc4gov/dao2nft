from ..parts.action_list import *


def p_liquidity_provision(params, substep, state_history, prev_state):
    """
    Provide liquidity.
    """
    agents = prev_state['agents']
    state = prev_state['state']

    lp_agents = {k: v for k, v in agents.items() if 'Liquidity Provider' in v.name}
 
    agent_delta = {}

    for label, agent in list(lp_agents.items()):
        agent.takeStep(state)
        agent_delta[label] = agent

    return {'agent_delta': agent_delta }

def s_liquidity_provision(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta in list(policy_input['agent_delta'].items()):
        updated_agents[label] = delta
    return ('agents', updated_agents)