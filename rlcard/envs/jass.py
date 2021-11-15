import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.base import Card
from rlcard.games.jass.utils import ACTION_LIST, CARD_VALUES, SUIT_OFFSET, one_hot_encode_cards, one_hot_encode_trump
from rlcard.games.jass import Game

DEFAULT_GAME_CONFIG = {
    'game_num_players': 4,
}

class JassEnv(Env):
    ''' Jass Environment
    '''

    def __init__(self, config):
        ''' Initialize the Blackjack environment
        '''
        self.name = 'jass'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()

        self.actions = ACTION_LIST

        super().__init__(config)

        # FIXME
        self.state_shape = [[36 + 36 + 36 + 6] for _ in range(self.num_players)]
        self.action_shape = [[36] for _ in range(self.num_players)]

    def _get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''

        legal_actions = self.game.state['actions']
        legal_actions = OrderedDict({self.actions.index(Card(action.suit, action.rank)): None for action in legal_actions})
        return legal_actions

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        current_hand = one_hot_encode_cards(state['current_hand'])
        others_hand = one_hot_encode_cards(state['others_hand'])
        played_cards = [one_hot_encode_cards(c) for c in state['played_cards']]
        trump = one_hot_encode_trump(state['trump'])

        obs = np.concatenate((
            current_hand,
            np.concatenate(others_hand),
            played_cards,
            trump
        ))

        extracted_state = OrderedDict({'obs': obs, 'legal_actions': self._get_legal_actions()})
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = [a for a in state['actions']]
        extracted_state['action_record'] = self.action_recorder
        return extracted_state


    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''
        return np.array(self.game.get_payoffs())

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['num_players'] = self.num_players
        state['hand_cards'] = [player.current_hand for player in self.game.players]
        state['played_cards'] = self.game.round.played_cards
        state['trump'] = self.game.round.trump
        state['current_player'] = self.game.round.current_player
        state['legal_actions'] = self.game.round.get_legal_actions(
            self.game.players, state['current_player'])
        return state



    def _decode_action(self, action_id):
        ''' Decode the action for applying to the game

        Args:
            action id (int): action id

        Returns:
            action (str): action for the game
        '''
        return self.actions[action_id]
