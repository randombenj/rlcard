# -*- coding: utf-8 -*-
''' Implement Doudizhu Dealer class
'''
import functools
from rlcard.games.jass import player

from rlcard.utils import init_32_deck
from rlcard.games.jass.utils import cards2str, did_push, get_jass_sort_card, get_jass_sort_card

class JassDealer:
    ''' Dealer will shuffle, deal cards, and determine players' roles
    '''
    def __init__(self, np_random):
        '''Give dealer the deck

        Notes:
            1. deck with 32 cards including black joker and red joker
        '''
        self.np_random = np_random
        self.deck = init_32_deck()
        # should work also for jass
        #self.deck.sort(key=functools.cmp_to_key(jass_sort_card))
        self.trump = None

    def shuffle(self):
        ''' Randomly shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, players):
        ''' Deal cards to players

        Args:
            players (list): list of Jass objects
        '''
        hand_num = (len(self.deck)) // len(players)
        for index, player in enumerate(players):
            current_hand = self.deck[index*hand_num:(index+1)*hand_num]
            #current_hand.sort(key=functools.cmp_to_key(jass_sort_card))
            player.set_current_hand(current_hand)
            player.initial_hand = cards2str(player.current_hand)

    def determine_trump(self, players, trump_player: int):
        ''' Determine trump according to players' hand

        Args:
            players (list): list of Jass objects

        Returns:
            int: the trump type
        '''
        # deal cards
        self.shuffle()
        self.deal_cards(players)
        
        self.trump = players[trump_player].set_trump()
        if did_push(self.trump):
            # colleague chooses trump 'schiebe'
            self.trump = player[trump_player + 2 % 4].set_trump()

        for player in players:
            player.current_hand.sort(key=functools.cmp_to_key(get_jass_sort_card(self.trump)))

        return self.trump
