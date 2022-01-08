from ..parts.metrics import *

def p_accounting(params, substep, state_history, prev_state):
    """
    Update the state and KPIs.
    """
    step = prev_state['timestep']
    # print(f'p_accounting, {step} - {substep}')

    state = prev_state['state']
    agents = prev_state['agents']

    state_delta = state

    return {'state_delta': state_delta }

def s_accounting(params, substep, state_history, prev_state, policy_input):
    updated_stats = policy_input['state_delta']
    return ('state', updated_stats)