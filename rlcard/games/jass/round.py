# -*- coding: utf-8 -*-
''' Implement Doudizhu Round class
'''

import functools
from typing import List, Tuple
import numpy as np
from rlcard.games.base import Card

from jass.game.const import color_of_card, color_masks, J_offset, higher_trump, lower_trump, card_values, UNE_UFE, \
    OBE_ABE, next_player, partner_player
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
        self.current_trick = 0
        self.tricks: List[List[JassPlayer, Card]] = [[] for _ in range(9)]
        self.trick_points: List[List[JassPlayer, int]] = [[] for _ in range(9)]
        self.trick_winner: List[List[int]] = [[0, 0, 0, 0] for _ in range(9)]
        self.trick_first_player: List[List[int]] = [[0, 0, 0, 0] for _ in range(9)]
        # cards lying on the table
        self.points: List[dict] = []

    def initiate(self, players):
        ''' Call dealer to deal cards and bid landlord.

        Args:
            players (list): list of JassPlayer objects
        '''
        self.trump, is_forehand = self.dealer.determine_trump(players, self.current_player)
        self.trick_first_player[self.current_trick][self.current_player] = 1
        self.public = {
            'trump': self.trump,
            'is_forehand': is_forehand,
            'current_trick': self.current_trick,
            'tricks': self.tricks,
            'trick_winner': self.trick_winner,
            'trick_first_player': self.trick_first_player,
            'played_cards': self.played_cards
        }

    def update_public(self):
        self.public['current_trick'] = self.current_trick
        self.public['tricks'] = self.tricks
        self.public['trick_winner'] = self.trick_winner
        self.public['trick_first_player'] = self.trick_first_player
        self.public['played_cards'] = self.played_cards

    def get_legal_actions(self, players, player_id):
        return get_legal_actions(
            hand=players[player_id].current_hand,
            table_cards=[c[1] for c in self.tricks[self.current_trick]],
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
        self.tricks[self.current_trick].append((player, action))
        self.played_cards[player.player_id] += f"{action.suit}{action.rank} "

        if len(self.tricks[self.current_trick]) == 4:
            # round is over
            self.current_player = self.count_points()
            self.trick_winner[self.current_trick][self.current_player] = 1
            self.current_trick += 1

            if not self.current_trick >= 8:
                # the first to choose is the wone who won the last round
                self.trick_first_player[self.current_trick][self.current_player] = 1
        else:
            self.current_player = (self.current_player + 1) % 4

        self.update_public()

        return self.current_player

    def count_points(self) -> int:
        """
        Count the current points of both teams and returns the winner id
        """
        # cross check
        from jass.game.rule_schieber import RuleSchieber
        from jass.game.const import card_ids
        rule = RuleSchieber()

        trick = [card_ids[f"{c.suit}{c.rank if c.rank != 'T' else '10'}"] for (p, c) in self.tricks[self.current_trick]]
        trump = TRUMP_TYPE_INDEX[self.trump]

        points = rule.calc_points(
            is_last=sum([len(c.split()) for c in self.played_cards]) == 36,
            trump=trump,
            trick=trick
        )

        print(f"CALC WINNER FOR TRICK: {trick}  {self.tricks[self.current_trick]}, {trump}, {self.trick_first_player} {np.argmax(self.trick_first_player[self.current_trick])}")

        winner_index = self.calc_winner(
            trump=trump,
            trick=trick,
        )

        winner_id = self.tricks[self.current_trick][winner_index][0].player_id
        self.points.append({"winner": winner_id, "points": points})
        return winner_id

    def calc_winner(self, trick: np.ndarray, trump: int = -1) -> int:
        """
        Calculate the winner of a completed trick.

        Second implementation in an attempt to be more efficient, while the implementation is somewhat longer
        and more complicated it is about 3 times faster than the previous method.

        Precondition:
            0 <= trick[i] <= 35, for i = 0..3
        Args:
            trick: the completed trick
            first_player: the first player of the trick
            trump: trump for the round
        Returns:
            the player who won this trick
        """
        color_of_first_card = color_of_card[trick[0]]
        if trump == UNE_UFE:
            # lowest card of first color wins
            winner = 0
            lowest_card = trick[0]
            for i in range(1, 4):
                # (lower card values have a higher card index)
                if color_of_card[trick[i]] == color_of_first_card and trick[i] > lowest_card:
                    lowest_card = trick[i]
                    winner = i
        elif trump == OBE_ABE:
            # highest card of first color wins
            winner = 0
            highest_card = trick[0]
            for i in range(1, 4):
                if color_of_card[trick[i]] == color_of_first_card and trick[i] < highest_card:
                    highest_card = trick[i]
                    winner = i
        elif color_of_first_card == trump:
            # trump mode and first card is trump: highest trump wins
            winner = 0
            highest_card = trick[0]
            for i in range(1, 4):
                # lower_trump[i,j] checks if j is a lower trump than i
                if color_of_card[trick[i]] == trump and lower_trump[trick[i], highest_card]:
                    highest_card = trick[i]
                    winner = i
        else:
            # trump mode, but different color played on first move, so we have to check for higher cards until
            # a trump is played, and then for the highest trump
            winner = 0
            highest_card = trick[0]
            trump_played = False
            trump_card = None
            for i in range(1, 4):
                if color_of_card[trick[i]] == trump:
                    if trump_played:
                        # second trump, check if it is higher
                        if lower_trump[trick[i], trump_card]:
                            winner = i
                            trump_card = trick[i]
                    else:
                        # first trump played
                        trump_played = True
                        trump_card = trick[i]
                        winner = i
                elif trump_played:
                    # color played is not trump, but trump has been played, so ignore this card
                    pass
                elif color_of_card[trick[i]] == color_of_first_card:
                    # trump has not been played and this is the same color as the first card played
                    # so check if it is higher
                    if trick[i] < highest_card:
                        highest_card = trick[i]
                        winner = i

        return winner