# -*- coding: utf-8 -*-
''' Implement Doudizhu Player class
'''
import functools

from rlcard.games.jass.utils import get_gt_cards
from rlcard.games.jass.utils import cards2str, jass_sort_card


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
        self.singles = '6789TJQKA'

        #record cards removed from self._current_hand for each play()
        # and restore cards back to self._current_hand when play_back()
        self._recorded_played_cards = []

    @property
    def current_hand(self):
        return self._current_hand

    def set_trump(self):
        # TODO:
        return "D"

    def set_current_hand(self, value):
        self._current_hand = value

    def get_state(self, public, others_hands, num_cards_left, actions):
        state = {}
        state['trump'] = public['trump']
        state['table_cards'] = public['table_cards'].copy()
        state['played_cards'] = public['played_cards']
        state['self'] = self.player_id
        state['current_hand'] = cards2str(self._current_hand)
        state['others_hand'] = others_hands
        state['num_cards_left'] = num_cards_left
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