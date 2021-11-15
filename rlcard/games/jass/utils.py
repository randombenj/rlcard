''' Doudizhu utils
'''
import os
import numpy as np
import json
from collections import OrderedDict
import threading
import collections
from typing import List

import rlcard
from rlcard.games.base import Card


VALID_SUIT = ['S', 'H', 'D', 'C']
VALID_RANK = ['A', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

ACTION_LIST = [Card(suit, rank) for rank in VALID_RANK for suit in VALID_SUIT]


def did_push(trump):
    return trump == "P"

def get_card_name_by_index(index: int) -> Card:
    valid_suit = ['S', 'H', 'D', 'C']
    valid_rank = ['A', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    actions = []
    for suit in valid_suit:
        for rank in valid_rank:
            actions.append(Card(suit, rank))

    return actions[index]

SUIT_OFFSET = {
    "D": 0,
    "H": 8,
    "S": 17,
    "C": 27
}
TRUMP = ['D', "H", "S", "C", "O", "U", "P"]
TRUMP_TYPE_INDEX = {'D': 0, "H": 1, "S": 2, "C": 3, "O": 4, "U": 5, "P": 6}

# rank list of solo character of cards
CARD_RANK_STR = ['6', '7', '8', '9', 'T', 'J', 'Q', 'K','A']
CARD_RANK_STR_INDEX = {
    '6': 0,
    '7': 1,
    '8': 2,
    '9': 3,
    'T': 4,
    'J': 5,
    'Q': 6,
    'K': 7,
    'A': 8
}

NUMBER_OF_CARDS = 36

TRUMP_RANK = ['6', '7', '8', 'T', 'Q', 'K', 'A', '9', 'J']
TRUMP_VALUE = {'6': 0, '7': 0, '8': 0, 'T': 10, 'Q': 3, 'K': 4, 'A': 11, '9': 14, 'J': 20}
TRUMP_INDEX = {'6': 0, '7': 1, '8': 2, 'T': 3, 'Q': 4, 'K': 5, 'A': 6, '9': 7, 'J': 8}

NORMAL_VALUE = {'6': 0, '7': 0, '8': 0, '9': 0, 'T': 10, 'J': 2, 'Q': 3, 'K': 4, 'A': 11}
UNE_VALUE = {'A': 0, 'K': 4, 'Q': 3, 'J': 2, 'T': 10, '9': 0, '8': 8, '7': 0, '6': 11}

CARD_INDEX = {
    "D": TRUMP_INDEX,
    "H": TRUMP_INDEX,
    "S": TRUMP_INDEX,
    "C": TRUMP_INDEX,
    "O": {'6': 0, '7': 1, '8': 2, '9': 3, 'T': 4, 'J': 5, 'Q': 6, 'K': 7, 'A': 8},
    "U": {'A': 0, 'K': 1, 'Q': 2, 'J': 3, 'T': 4, '9': 5, '8': 6, '7': 7, '6': 8}
}
CARD_VALUES = {
    "D": TRUMP_VALUE,
    "H": TRUMP_VALUE,
    "S": TRUMP_VALUE,
    "C": TRUMP_VALUE,
    "O": NORMAL_VALUE,
    "U": UNE_VALUE
}

# rank list
CARD_RANK = {
    "D": TRUMP_RANK,
    "H": TRUMP_RANK,
    "S": TRUMP_RANK,
    "C": TRUMP_RANK,
    "O": ['6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'],
    "U": ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6']
}

def one_hot_encode_trump(trump: str):
    one_hot = np.zeros(6)
    one_hot[TRUMP.index(trump)] = 1
    return one_hot


def one_hot_encode_cards(cards: str):
    one_hot = np.zeros(36)
    for card in cards.split():
        suit, rank = card[0], card[1]
        one_hot[SUIT_OFFSET[suit] + CARD_RANK_STR_INDEX[rank]] = 1
    return one_hot

#INDEX = OrderedDict(sorted(INDEX.items(), key=lambda t: t[1]))

def get_higher_trump(trump_cards: List[Card], trump: Card) -> List[Card]:
    rank_index = CARD_RANK[trump.suit].index(trump.rank)
    return [t for t in trump_cards if CARD_RANK[trump.suit].index(t.rank) > rank_index]

def get_lower_trump(trump_cards: List[Card], trump: Card) -> List[Card]:
    rank_index = CARD_RANK[trump.suit].index(trump.rank)
    return [t for t in trump_cards if CARD_RANK[trump.suit].index(t.rank) < rank_index]

def jass_sort_str(card_1, card_2):
    ''' Compare the rank of two cards of str representation

    Args:
        card_1 (str): str representation of solo card
        card_2 (str): str representation of solo card

    Returns:
        int: 1(card_1 > card_2) / 0(card_1 = card2) / -1(card_1 < card_2)
    '''
    key_1 = CARD_RANK_STR.index(card_1)
    key_2 = CARD_RANK_STR.index(card_2)
    if key_1 > key_2:
        return 1
    if key_1 < key_2:
        return -1
    return 0


def get_jass_sort_card(trump):
    def __jass_sort_card(card_1, card_2):
        ''' Compare the rank of two cards of Card object

        Args:
            card_1 (object): object of Card
            card_2 (object): object of card
        '''

        # if one is trump and the other not, trump is more valuable
        if card_1.suit == trump and card_2.suit != trump:
            return 1
        if card_1.suit != trump and card_2.suit == trump:
            return -1

        # unne
        if trump == "U":
            key = []
            for card in [card_1, card_2]:
                key.append(CARD_RANK["U"].index(card.rank))

            if key[0] > key[1]:
                return 1
            if key[0] < key[1]:
                return -1
            return 0


        # both are trumps, so compare trumps
        if card_1.suit == trump and card_2.suit == trump:
            key = []
            for card in [card_1, card_2]:
                key.append(CARD_RANK[trump].index(card.rank))

            if key[0] > key[1]:
                return 1
            if key[0] < key[1]:
                return -1
            return 0

        # default case, obe abe
        key = []
        for card in [card_1, card_2]:
            key.append(CARD_RANK["O"].index(card.rank))

        if key[0] > key[1]:
            return 1
        if key[0] < key[1]:
            return -1
        return 0

    return __jass_sort_card


def cards2str_with_suit(cards):
    ''' Get the corresponding string representation of cards with suit

    Args:
        cards (list): list of Card objects

    Returns:
        string: string representation of cards
    '''
    return ' '.join([card.suit+card.rank for card in cards])

def cards2str(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of Card objects

    Returns:
        string: string representation of cards
    '''
    response = ''
    for card in cards:
        if card.rank == '':
            response += card.suit[0]
        else:
            response += card.rank
    return response

class LocalObjs(threading.local):
    def __init__(self):
        self.cached_candidate_cards = None
_local_objs = LocalObjs()

def contains_cards(candidate, target):
    ''' Check if cards of candidate contains cards of target.

    Args:
        candidate (string): A string representing the cards of candidate
        target (string): A string representing the number of cards of target

    Returns:
        boolean
    '''
    # In normal cases, most continuous calls of this function
    #   will test different targets against the same candidate.
    # So the cached counts of each card in candidate can speed up
    #   the comparison for following tests if candidate keeps the same.
    if not _local_objs.cached_candidate_cards or _local_objs.cached_candidate_cards != candidate:
        _local_objs.cached_candidate_cards = candidate
        cards_dict = collections.defaultdict(int)
        for card in candidate:
            cards_dict[card] += 1
        _local_objs.cached_candidate_cards_dict = cards_dict
    cards_dict = _local_objs.cached_candidate_cards_dict
    if (target == ''):
        return True
    curr_card = target[0]
    curr_count = 1
    for card in target[1:]:
        if (card != curr_card):
            if (cards_dict[curr_card] < curr_count):
                return False
            curr_card = card
            curr_count = 1
        else:
            curr_count += 1
    if (cards_dict[curr_card] < curr_count):
        return False
    return True

def encode_cards(plane, cards):
    ''' Encode cards and represerve it into plane.

    Args:
        cards (list or str): list or str of cards, every entry is a
    character of solo representation of card
    '''
    if not cards:
        return None
    layer = 1
    if len(cards) == 1:
        rank = CARD_RANK_STR.index(cards[0])
        plane[layer][rank] = 1
        plane[0][rank] = 0
    else:
        for index, card in enumerate(cards):
            if index == 0:
                continue
            if card == cards[index-1]:
                layer += 1
            else:
                rank = CARD_RANK_STR.index(cards[index-1])
                plane[layer][rank] = 1
                layer = 1
                plane[0][rank] = 0
        rank = CARD_RANK_STR.index(cards[-1])
        plane[layer][rank] = 1
        plane[0][rank] = 0

import numpy as np
import random

from jass.game.game_observation import GameObservation
from jass.game.game_state_util import state_from_observation
from jass.game.game_sim import GameSim
from jass.game.game_util import convert_one_hot_encoded_cards_to_int_encoded_list, get_cards_encoded
from jass.game.const import color_of_card
from jass.game.const import *


# Score for each card of a color from Ace to 6
# score if the color is trump
trump_score = [15, 10, 7, 25, 6, 19, 5, 5, 5]
# score if the color is not trump
no_trump_score = [9, 7, 5, 2, 1, 0, 0, 0, 0]
# score if obenabe is selected (all colors)
obenabe_score = [14, 10, 8, 7, 5, 0, 5, 0, 0,]
# score if uneufe is selected (all colors)
uneufe_score = [0, 2, 1, 1, 5, 5, 7, 9, 11]

# jass is played counter clock wise so when player 3 starts next player is player 2
def get_previous_player(current_player):
    return current_player + 1 if current_player != 3 else 0

def get_next_player(current_player):
    return current_player - 1 if current_player != 0 else 3

def calculate_trump_selection_score(cards, trump: int) -> int:
    hand_int = convert_one_hot_encoded_cards_to_int_encoded_list(cards)
    score = 0
    for card in hand_int:
        color = color_of_card[card]
        offset = offset_of_card[card]
        if color == trump:
            score += trump_score[offset]
        else:
            score += no_trump_score[offset]
    return score

def calculate_obenabe_selection_score(cards) -> int:
    hand_int = convert_one_hot_encoded_cards_to_int_encoded_list(cards)
    score = 0
    for card in hand_int:
        offset = offset_of_card[card]
        score += obenabe_score[offset]
    return score

def calculate_uneufe_selection_score(cards) -> int:
    hand_int = convert_one_hot_encoded_cards_to_int_encoded_list(cards)
    score = 0
    for card in hand_int:
        offset = offset_of_card[card]
        score += uneufe_score[offset]
    return score

def get_trump_based_on_selection_scores(hand, forehand) -> int:
    # data conversion from our hand to jasskit onehot
    old_hand = hand
    hand = np.zeros(36)
    for h in old_hand:
        hand[card_ids[f"{h.suit}{'10' if h.rank == 'T' else h.rank}"]] = 1

    scores = [calculate_trump_selection_score(hand, trump) for trump in [D, H, S, C]]
    scores.append(calculate_obenabe_selection_score(hand))
    scores.append(calculate_uneufe_selection_score(hand))
    best_score = np.max(scores)
    result = None
    if (best_score < 68) & (forehand != 0):
        result = PUSH_ALT
    else:
        result = np.argmax(scores)

    # convert to int as json serialization can't handle numpy datatypes
    return int(result)

def get_smallest_card(cards_int) -> int:
    smallest_card = None
    for card in cards_int:
        offset = offset_of_card[card]
        if (smallest_card is None):
            smallest_card = card
        elif (offset_of_card[smallest_card] < offset):
            smallest_card = card
    return smallest_card

def get_highest_card(cards_int) -> int:
    highest_card = None
    for card in cards_int:
        offset = offset_of_card[card]
        if (highest_card is None):
            highest_card = card
        elif (offset_of_card[highest_card] > offset):
            highest_card = card
    return highest_card

def get_highest_trump(trumps) -> int:
    trump = color_of_card[trumps[0]]
    if np.isin(color_offset[trump] + J_offset, trumps):
        return color_offset[trump] + J_offset
    elif np.isin(color_offset[trump] + Nine_offset, trumps):
        return color_offset[trump] + Nine_offset
    else:
        return np.min(trumps)

def get_cards_from_color(cards_int, color):
    cards_with_given_color = []
    for card in cards_int:
        if color_of_card[card] == color:
            cards_with_given_color.append(card)
    return cards_with_given_color


def random_play_to_the_end(gameSim : GameSim):
    '''
    Returns the GameState of finished game. Cards are played random but trump decision is based on selection scores.
    '''
    # simulate playing the game to the end with random moves
    while not gameSim.is_done():
        obs = gameSim.get_observation()
        if gameSim.state.trump < 0:
            trump = get_trump_based_on_selection_scores(obs.hand, obs.forehand)
            gameSim.action_trump(trump)
        else:
            valid_cards = gameSim.rule.get_valid_cards_from_obs(obs)
            card = np.random.default_rng().choice(np.flatnonzero(valid_cards))
            gameSim.action_play_card(card)
    return gameSim.state

def get_game_state_with_random_hand_for_other_players(obs : GameObservation):
    # create random hand cards for the other players
    hands = get_random_hand_for_other_players(obs)
    # create GameState based on given observation with random hand cards 
    # for the other players
    gameState = state_from_observation(obs, hands)
    return gameState

def get_random_hand_for_other_players(obs : GameObservation):
    hands_one_hot_encoded = np.zeros(shape=[4, 36], dtype=np.int32)
    hands = dict([
        (0, []),
        (1, []),
        (2, []),
        (3, [])
    ])

    if obs.player_view != obs.player:
        Exception("Player view belongs not to player whos turn it is!")
    
    available_cards_one_hot_encoded = get_available_cards_from_observation(obs)
    cards = np.flatnonzero(available_cards_one_hot_encoded).tolist()
    first_of_trick = obs.trick_first_player[obs.nr_tricks]
    last_of_trick = first_of_trick + 1 if first_of_trick != 3 else 0

    random.shuffle(cards)
    for card in cards:
        #print(last_of_trick)
        if last_of_trick == obs.player:
            last_of_trick = get_previous_player(last_of_trick)
        hands[last_of_trick].append(card)
        last_of_trick = get_previous_player(last_of_trick)
    
    players = [0, 1, 2, 3]
    players.remove(obs.player)
    hands_one_hot_encoded[obs.player] = obs.hand
    for p in players:
        hands_one_hot_encoded[p] = get_cards_encoded(hands[p])
    
    return hands_one_hot_encoded


def get_available_cards_from_observation(obs : GameObservation) -> np.ndarray:
    '''
    returns:
        Available cards in this game observation as one hot encoded array.
    '''
    available_cards = np.ones(shape=[36], dtype=np.int32)
    # remove already played cards
    for trick in obs.tricks:
        for card in trick:
            if(card >= 0):
                available_cards[card] = 0
    # remove cards from current unfinished trick
    for card in obs.current_trick:
        if(card >= 0):
            available_cards[card] = 0
    # remove cards of player we know the hand
    for card in np.flatnonzero(obs.hand):
        available_cards[card] = 0
    return available_cards
