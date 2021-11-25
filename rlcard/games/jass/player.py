# -*- coding: utf-8 -*-
''' Implement Doudizhu Player class
'''
import functools

from rlcard.games.jass.utils import TRUMP, cards2str_with_suit, get_trump_based_on_selection_scores
from rlcard.games.jass.utils import cards2str, get_jass_sort_card


class JassPlayer:
    ''' Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom corresponding action
    '''
    def __init__(self, player_id, np_random):
        ''' Give the player an id in one game

        Args:
            player_id (int): the player_id of a player

        Notes:
            2. played_cards: The cards played in one round
            3. hand: Initial cards
            4. _current_hand: The rest of the cards after playing some of them
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.initial_hand = None
        self._current_hand = []
        self.played_cards = None

        #record cards removed from self._current_hand for each play()
        # and restore cards back to self._current_hand when play_back()
        self._recorded_played_cards = []

    @property
    def current_hand(self):
        return self._current_hand

    def set_trump(self, is_forehand=True):
        result = get_trump_based_on_selection_scores(self._current_hand, 0 if is_forehand else -1)
        return TRUMP[result]

    def set_current_hand(self, value):
        self._current_hand = value

    def get_state(self, public, others_hands, actions):
        state = {}

        state['trump'] = public['trump']
        state['is_forehand'] = public['is_forehand']
        state['trick_winner'] = public['trick_winner'].copy()
        state['trick_first_player'] = public['trick_first_player'].copy()
        state['current_trick'] = public['current_trick']
        state['tricks'] = public['tricks'].copy()
        state['self'] = self.player_id
        state['current_hand'] = cards2str_with_suit(self._current_hand)
        state['others_hand'] = others_hands
        state['actions'] = actions

        return state

    def available_actions(self, judger, trump, table_cards):
        ''' Get the actions can be made based on the rules

        Args:
            greater_player (JassPlayer object): player who played
        current biggest cards.
            judger (JassJudger object): object of JassJudger

        Returns:
            list: list of string of actions. Eg: ['8', '9', 'T', 'J']
        '''

        actions = judger.get_playable_cards(self, trump, table_cards)
        return actions

    def play(self, action):
        ''' Perfrom action

        Args:
            action (string): specific action
            greater_player (DoudizhuPlayer object): The player who played current biggest cards.

        Returns:
            object of DoudizhuPlayer: If there is a new greater_player, return it, if not, return None
        '''
        self._current_hand.remove(action)

    def __repr__(self):
        return f"Player({self.player_id})"