
import numpy as np

from rlcard.games.base import Card
from rlcard.games.jass.utils import ACTION_LIST


class HumanAgent(object):
    ''' A human agent for Leduc Holdem. It can be used to play against trained models
    '''

    def __init__(self, num_actions):
        ''' Initilize the human agent

        Args:
            num_actions (int): the size of the ouput action space
        '''
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        '''
        #print(state['raw_obs'])
        _print_state(state, state['action_record'])
        action = input('>> You choose action (card): ')
        action_card = Card(suit=action[0], rank=action[1])
        while action_card not in state['raw_legal_actions']:
            print('Action illegel...')
            action = input('>> Re-choose action (card): ')
            action_card = Card(suit=action[0], rank=action[1])

        return action_card
        print(state['raw_legal_actions'], ACTION_LIST.index(action_card))
        return state['raw_legal_actions'][ACTION_LIST.index(action_card)]

    def eval_step(self, state):
        ''' Predict the action given the curent state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state), {}

def _print_state(state, action_record):
    ''' Print out the state of a given player

    Args:
        player (int): Player id
    '''
    #_action_list = []
    #for i in range(1, len(action_record)+1):
    #    if action_record[-i][0] == state['current_player']:
    #        break
    #    _action_list.insert(0, action_record[-i])
    #for pair in _action_list:
    #    print(f'>> Player {pair[0]} chooses ', end='')

    print('=============== Cards on Table ===============')
    print(f"First player: {np.argmax(state['raw_obs']['trick_first_player'][state['raw_obs']['current_trick']])}")
    if not state['raw_obs']['current_trick'] == 0:
        print(f"Last round winner: {np.argmax(state['raw_obs']['trick_winner'][state['raw_obs']['current_trick'] - 1])}")
    print(f"Trump: {state['raw_obs']['trump']}  =>  {', '.join([str(a[1]) for a in state['raw_obs']['tricks'][state['raw_obs']['current_trick']]])}")
    print('\n=============== Your Hand ===============')
    print(state["raw_obs"]['current_hand'])
    print('')
    print('======== Actions You Can Choose =========')
    print(", ".join([str(ACTION_LIST[i]) for i, a in state['legal_actions'].items()]))
    print('\n')
