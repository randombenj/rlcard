# -*- coding: utf-8 -*-
''' Implement Doudizhu Judger class
'''
from typing import List, Tuple
import numpy as np
import collections
from itertools import combinations
from bisect import bisect_left
from rlcard.games.jass.player import JassPlayer

from rlcard.games.base import Card
from rlcard.games.jass.utils import CARD_RANK_STR, CARD_RANK_STR_INDEX, get_legal_actions
from rlcard.games.jass.utils import SUIT_OFFSET, TRUMP_INDEX, TRUMP_TYPE_INDEX, cards2str, get_higher_trump, get_lower_trump, get_jass_sort_card
from rlcard.games.jass.utils import cards2str, contains_cards



class JassJudger:
    ''' Determine what cards a player can play
    '''

    
    def __init__(self, players, np_random):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        self.playable_cards = [set() for _ in range(4)]
        self._recorded_removed_playable_cards = [[] for _ in range(3)]
        for player in players:
            player_id = player.player_id
            current_hand = cards2str(player.current_hand)
            self.playable_cards[player_id] = [] #self.playable_cards_from_hand(current_hand)

    @staticmethod
    def judge_game(players, player_id):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        player = players[player_id]
        if not player.current_hand:
            return True
        return False

    @staticmethod
    def get_playable_cards(player: JassPlayer, trump: str, table_cards: List[Tuple[JassPlayer, Card]]) -> List[Card]:
        return get_legal_actions(
            hand=player.current_hand, 
            table_cards=[c[1] for c in table_cards],
            trump=trump
        )
