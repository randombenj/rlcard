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
from rlcard.games.jass.utils import CARD_RANK_STR, CARD_RANK_STR_INDEX
from rlcard.games.jass.utils import SUIT_OFFSET, TRUMP_INDEX, TRUMP_TYPE_INDEX, cards2str, get_higher_trump, get_lower_trump, jass_sort_card
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
        hand = player.current_hand
        table_cards = [c[1] for c in table_cards]
        move_nr = len(table_cards)

        # play anything on the first move
        if move_nr == 0:
            return hand

        # get the color of the first played card and check if we have that color
        color_played = table_cards[0].suit
        color_hand = [c for c in hand if c.suit == color_played]
        have_color_played = any(color_hand) 

        if TRUMP_TYPE_INDEX[trump] >= 4:
            # obe or une declared
            if have_color_played:
                # must give the correct color
                return color_hand
            else:
                # play anything, if we don't have the color
                return hand
        else:
            #
            # round with trumps declared (not 'obe' or 'une')
            #

            # check number of trumps we have and number of cards left, in order to simplify some of the conditions
            number_of_trumps = len(color_hand)
            number_of_cards = len(hand)

            #
            # the played color was trump
            #
            if color_played == trump:
                if number_of_trumps == 0:
                    # no more trumps, play anything
                    return hand
                elif number_of_trumps == 1:
                    if Card(trump, 'J') in hand:
                        # we have only trump jack, so we can play anything
                        return hand
                    else:
                        # we have just one trump and must play it
                        return [h for h in hand if h.suit == trump]
                else:
                    # we have more than one trump, so we must play one of them
                    return [h for h in hand if h.suit == trump]
            #
            # the played color was not trump
            #
            else:
                # check if anybody else (player 1 or player 2) played a trump, and if yes how high
                lowest_trump_played = None
                trump_played = False

                if move_nr > 1:
                    # check player 1
                    if table_cards[1].suit == trump:
                        trump_played = True
                        lowest_trump_played = table_cards[1]
                    # check player 2
                    if move_nr == 3:
                        if table_cards[2].suit == trump:
                            trump_played = True
                            if lowest_trump_played is not None:
                                # 2 trumps were played, so we must compare
                                if TRUMP_INDEX[lowest_trump_played.rank] < TRUMP_INDEX[table_cards[2].rank]:
                                    # move from player 2 is lower (as its index value is higher)
                                    lowest_trump_played = table_cards[2]
                            else:
                                # this is the only trump played, so it is the lowest
                                lowest_trump_played = table_cards[2]

                #
                # nobody played a trump, so we do not need to consider any restrictions on playing trump ourselves
                #
                if not trump_played:
                    if have_color_played:
                        # must give a color or can give any trump
                        trump_cards = [h for h in hand if h.suit == trump]
                        return color_hand + trump_cards
                    else:
                        # we do not have the color, so we can play anything, including any trump
                        return hand

                #
                # somebody played a trump, so we have the restriction that we can not play a lower trump, with
                # the exception if we only have trump left
                #
                else:
                    if number_of_trumps == number_of_cards:
                        # we have only trump left, so we can give any of them
                        return hand
                    else:
                        #
                        # find the valid trumps to play
                        #

                        # all trumps in hand
                        trump_cards = [h for h in hand if h.suit == trump]

                        # higher trump cards in hand
                        higher_trump_cards = get_higher_trump(trump_cards, lowest_trump_played)

                        # lower trump cards in hand
                        lower_trump_cards = get_lower_trump(trump_cards, lowest_trump_played)

                    if have_color_played:
                        # must give a color or a higher trump
                        return color_hand + higher_trump_cards
                    else:
                        # play anything except a lower trump
                        return [c for c in hand if c != lower_trump_cards]

    @staticmethod
    def judge_payoffs(players):
        payoffs = np.array([0, 0, 0])
        if winner_id == landlord_id:
            payoffs[landlord_id] = 1
        else:
            for index, _ in enumerate(payoffs):
                if index != landlord_id:
                    payoffs[index] = 1
        return payoffs
