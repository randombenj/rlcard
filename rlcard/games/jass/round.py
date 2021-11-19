# -*- coding: utf-8 -*-
''' Implement Doudizhu Round class
'''

import functools
from typing import List, Tuple
import numpy as np
from rlcard.games.base import Card

from rlcard.games.jass import Dealer, Player
from rlcard.games.jass.player import JassPlayer
from rlcard.games.jass.utils import CARD_VALUES, SUIT_OFFSET, TRUMP_INDEX, TRUMP_TYPE_INDEX, TRUMP_VALUE, cards2str, get_higher_trump, get_legal_actions, get_lower_trump, get_jass_sort_card
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
        return get_legal_actions(
            hand=players[player_id].current_hand, 
            table_cards=[c[1] for c in self.table_cards],
            trump=self.trump
        )

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
        self.played_cards[player.player_id] += f"{action.suit}{action.rank} "

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
         # cross check
        from jass.game.rule_schieber import RuleSchieber
        from jass.game.const import card_ids
        rule = RuleSchieber()

        trick = [card_ids[f"{c.suit}{c.rank if c.rank != 'T' else '10'}"] for (p, c) in self.table_cards]
        trump = TRUMP_TYPE_INDEX[self.trump]
        first_player_id = self.table_cards[0][0].player_id

        points = rule.calc_points(
            is_last=sum([len(c.split()) for c in self.played_cards]) == 36,
            trump=trump,
            trick=trick
        )

        winner_id = rule.calc_winner(
            trump=trump,
            trick=trick,
            first_player=first_player_id
        )

        self.points.append({"winner": winner_id, "points": points})

        return winner_id

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


       

        p1 = sum([p for (_, p) in points])
        print(f"{p} == {p1}")
        assert p == p1

        self.points.append({"winner": winner.player_id, "points": points})

        """

        return winner.player_id
