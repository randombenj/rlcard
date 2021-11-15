# -*- coding: utf-8 -*-
''' Implement Doudizhu Round class
'''

import functools
from typing import List, Tuple
import numpy as np
from rlcard.games.base import Card

from rlcard.games.jass import Dealer, Player
from rlcard.games.jass.player import JassPlayer
from rlcard.games.jass.utils import CARD_VALUES, SUIT_OFFSET, TRUMP_INDEX, TRUMP_TYPE_INDEX, cards2str, get_higher_trump, get_lower_trump, get_jass_sort_card
from rlcard.games.jass.utils import CARD_INDEX, CARD_RANK_STR_INDEX


class JassRound:
    ''' Round can call other Classes' functions to keep the game running
    '''
    def __init__(self, np_random, played_cards):
        self.np_random = np_random
        self.played_cards = played_cards
        self.current_player = 0

        self.dealer = Dealer(self.np_random)
        # cards lying on the table
        self.table_cards: List[Tuple[JassPlayer, Card]] = []
        self.points: List[dict] = []

    def initiate(self, players):
        ''' Call dealer to deal cards and bid landlord.

        Args:
            players (list): list of JassPlayer objects
        '''
        self.trump = self.dealer.determine_trump(players, self.current_player)
        self.public = {
            'trump': self.trump,
            'table_cards': self.table_cards,
            'played_cards': self.played_cards
        }

    def get_legal_actions(self, players, player_id):
        hand = players[player_id].current_hand
        table_cards = [c[1] for c in self.table_cards]
        trump = self.trump
        move_nr = len(table_cards)

        # play anything on the first move
        if move_nr == 0:
            return hand

        # get the color of the first played card and check if we have that color
        color_played = table_cards[0].suit
        color_hand = [c for c in hand if c.suit == color_played]
        have_color_played = any(color_hand)

        if TRUMP_TYPE_INDEX[self.trump] >= 4:
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



    def proceed_round(self, player, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of JassPlayer
            action (str): string of legal specific action

        Returns:
            object of JassPlayer: player who played current biggest cards.
        '''

        player.play(action)
        self.table_cards.append((player, action))
        self.played_cards[player.player_id] += f"{action.suit}{action.rank}"

        if len(self.table_cards) == 4:
            # round is over
            self.current_player = self.count_points()
            self.table_cards = []
        else:
            self.current_player = (self.current_player + 1) % 4

        return self.current_player


    def count_points(self) -> int:
        """
        Count the current points of both teams and returns the winner id
        """
        points = []
        winner = None
        for player, card in self.table_cards:
            if self.trump == card.suit:
                point = CARD_VALUES[self.trump][card.rank]
            else:
                if self.trump == "U":
                    point = CARD_VALUES["U"][card.rank]
                else:
                    point = CARD_VALUES["O"][card.rank]
            points.append((player, point))

        # calculate winner of the round

        #import pdb; pdb.set_trace()
        trump_cards_in_round = [(p, c) for (p, c) in self.table_cards if c.suit == self.trump]
        if any(trump_cards_in_round):
            # if trump was played, the winner is the highest trump
            winner, _ = sorted(trump_cards_in_round, key=lambda p_c: TRUMP_INDEX[p_c[1].rank], reverse=True)[0]
        else:
            base_suit = self.table_cards[0][1].suit
            suit_cards_in_round = [(p, c) for (p, c) in self.table_cards if c.suit == base_suit]
            if self.trump == "U":
                winner, _ = sorted(suit_cards_in_round, key=lambda p_c: CARD_INDEX["U"][p_c[1].rank], reverse=True)[0]
            else:
                winner, _ = sorted(suit_cards_in_round, key=lambda p_c: CARD_INDEX["O"][p_c[1].rank], reverse=True)[0]

        self.points.append({"winner": winner.player_id, "points": points})

        return winner.player_id
