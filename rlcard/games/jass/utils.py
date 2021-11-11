''' Doudizhu utils
'''
import os
import json
from collections import OrderedDict
import threading
import collections
from typing import List

import rlcard
from rlcard.games.base import Card

"""
# Read required docs
ROOT_PATH = rlcard.__path__[0]

if not os.path.isfile(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/action_space.txt')) \
        or not os.path.isfile(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/card_type.json')) \
        or not os.path.isfile(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/type_card.json')):
    import zipfile
    with zipfile.ZipFile(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata.zip'),"r") as zip_ref:
        zip_ref.extractall(os.path.join(ROOT_PATH, 'games/doudizhu/'))

# Action space
action_space_path = os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/action_space.txt')
with open(action_space_path, 'r') as f:
    ID_2_ACTION = f.readline().strip().split()
    ACTION_2_ID = {}
    for i, action in enumerate(ID_2_ACTION):
        ACTION_2_ID[action] = i

# a map of card to its type. Also return both dict and list to accelerate
card_type_path = os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/card_type.json')
with open(card_type_path, 'r') as f:
    data = json.load(f, object_pairs_hook=OrderedDict)
    CARD_TYPE = (data, list(data), set(data))

# a map of type to its cards
type_card_path = os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/type_card.json')
with open(type_card_path, 'r') as f:
    TYPE_CARD = json.load(f, object_pairs_hook=OrderedDict)

"""

def did_push(trump):
    return trump == "P"

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
TRUMP_INDEX = {'6': 0, '7': 1, '8': 2, 'T': 3, 'Q': 4, 'K': 5, 'A': 6, '9': 7, 'J': 8}


CARD_INDEX = {
    "D": TRUMP_INDEX,
    "H": TRUMP_INDEX,
    "S": TRUMP_INDEX,
    "C": TRUMP_INDEX,
    "O": {
        '6': 0, 
        '7': 1,
        '8': 2,
        '9': 3, 
        'T': 4, 
        'J': 5, 
        'Q': 6,
        'K': 7, 
        'A': 8
    },
    "U": {'A': 0, 'K': 1, 'Q': 2, 'J': 3, 'T': 4, '9': 5, '8': 6, '7': 7, '6': 8}
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


def jass_sort_card(card_1, card_2):
    ''' Compare the rank of two cards of Card object

    Args:
        card_1 (object): object of Card
        card_2 (object): object of card
    '''
    key = []
    for card in [card_1, card_2]:
        if card.rank == '':
            key.append(CARD_RANK.index(card.suit))
        else:
            key.append(CARD_RANK.index(card.rank))
    if key[0] > key[1]:
        return 1
    if key[0] < key[1]:
        return -1
    return 0


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


def get_gt_cards(player, greater_player, trump):
    ''' Provide player's cards which are greater than the ones played by
    previous player in one round

    Args:
        player (JassPlayer object): the player waiting to play cards
        greater_player (JassPlayer object): the player who played current biggest cards.
        trump (int): the current trump

    Returns:
        list: list of string of greater cards
    '''
    # add 'pass' to legal actions
    gt_cards = []
    current_hand = cards2str(player.current_hand)
    target_cards = greater_player.played_cards
    target_types = CARD_TYPE[0][target_cards]
    type_dict = {}
    for card_type, weight in target_types:
        if card_type not in type_dict:
            type_dict[card_type] = weight
    if 'rocket' in type_dict:
        return gt_cards
    type_dict['rocket'] = -1
    if 'bomb' not in type_dict:
        type_dict['bomb'] = -1
    for card_type, weight in type_dict.items():
        candidate = TYPE_CARD[card_type]
        for can_weight, cards_list in candidate.items():
            if int(can_weight) > int(weight):
                for cards in cards_list:
                    # TODO: improve efficiency
                    if cards not in gt_cards and contains_cards(current_hand, cards):
                        # if self.contains_cards(current_hand, cards):
                        gt_cards.append(cards)
    return gt_cards
