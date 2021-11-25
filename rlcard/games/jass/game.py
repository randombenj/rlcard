# -*- coding: utf-8 -*-
''' Implement Doudizhu Game class
'''
import functools
from heapq import merge
import numpy as np

from rlcard.games.jass.utils import cards2str, NUMBER_OF_CARDS, cards2str_with_suit, get_jass_sort_card, CARD_RANK_STR
from rlcard.games.jass import Player
from rlcard.games.jass import Round
from rlcard.games.jass import Judger


class JassGame:
    ''' Provide game APIs for env to run jass and get corresponding state
    information.
    '''
    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 4

    def init_game(self):
        ''' Initialize players and state.

        Returns:
            dict: first state in one game
            int: current player's id
        '''
        # initialize public variables
        self.finished = False
        self.history = []

        self.teams = [[1, 3], [2, 4]]

        # initialize players
        self.players = [Player(num, self.np_random)
                        for num in range(self.num_players)]

        # initialize round to deal cards and determine trump
        self.played_cards = ["" for _ in range(self.num_players)]
        self.round = Round(self.np_random, self.played_cards)
        self.round.initiate(self.players)

        # initialize judger
        self.judger = Judger(self.players, self.np_random)

        # get state of first player
        player_id = self.round.current_player
        self.state = self.get_state(player_id)

        return self.state, player_id

    def step(self, action):
        ''' Perform one draw of the game

        Args:
            action (str): specific action of jass

        Returns:
            dict: next player's state
            int: next player's id
        '''
        if self.allow_step_back:
            # TODO: don't record game.round, game.players, game.judger if allow_step_back not set
            pass

        # perfrom action
        player = self.players[self.round.current_player]
        next_id = self.round.proceed_round(player, action)

        if self.judger.judge_game(self.players, self.round.current_player):
            # ROUND OVER
            self.finished = True

        # get next state
        state = self.get_state(next_id)
        self.state = state

        return state, next_id


    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''
        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        player = self.players[player_id]
        others_hands = self._get_others_current_hand(player)
        num_cards_left = [len(self.players[i].current_hand) for i in range(self.num_players)]
        if self.is_over():
            actions = []
        else:
            actions = list(player.available_actions(self.judger, self.round.trump, self.round.tricks[self.round.current_trick]))

        state = player.get_state(self.round.public, others_hands, actions)

        return state

    @staticmethod
    def get_num_actions():
        ''' Return the total number of abstract acitons

        Returns:
            int: the total number of actions in jass
        '''
        return 36

    def get_player_id(self):
        ''' Return current player's id

        Returns:
            int: current player's id
        '''
        return self.round.current_player

    def get_num_players(self):
        ''' Return the number of players in doudizhu

        Returns:
            int: the number of players in doudizhu
        '''
        return self.num_players

    def is_over(self):
        ''' Judge whether a game is over

        Returns:
            Bool: True(over) / False(not over)
        '''
        return self.finished

    def get_payoffs(self):
        team_points = [0, 0]
        for p in self.round.points:
            team_id = 0 if p["winner"] in self.teams[0] else 1
            team_points[team_id] += p["points"]

        point_difference = team_points[0] - team_points[1]
        payoff = point_difference / 157

        return [
            payoff,       # team 0 p1
            payoff * -1,  # team 1 p1
            payoff,       # team 0 p2
            payoff * -1,  # team 1 p2
        ]


    def _get_others_current_hand(self, player):
        other_player_1 = self.players[(player.player_id+1) % len(self.players)]
        teammate = self.players[(player.player_id+2) % len(self.players)]
        other_player_2 = self.players[(player.player_id+3) % len(self.players)]
        others_hand = merge(
            other_player_1.current_hand, teammate.current_hand, other_player_2.current_hand,
            key=functools.cmp_to_key(get_jass_sort_card(self.round.trump))
        )
        return cards2str_with_suit(others_hand)