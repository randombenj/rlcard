import numpy as np
from rlcard.games.jass.game import JassGame as Game


def test_get_num_player():
    game = Game()
    num_players = game.get_num_players()
    assert num_players == 4

def test_get_num_actions():
    game = Game()
    num_actions = game.get_num_actions()
    assert num_actions == 36

def test_init_game():
    game = Game()
    state, _ = game.init_game()

def test_get_player_id():
    game = Game()
    _, player_id = game.init_game()
    current = game.get_player_id()
    assert player_id == current


def test_get_legal_actions():
    game = Game()
    game.init_game()
    actions = game.get_legal_actions()
    assert len(actions) == 9

def test_step():
    game = Game()
    game.init_game()
    action = np.random.choice(game.get_legal_actions())
    previous_player_id = game.round.current_player
    state, next_player_id = game.step(action)
    current = game.round.current_player

    assert len(state['played_cards']) == 4
    assert next_player_id == current
    assert current != previous_player_id

def test_get_payoffs():
    game = Game()
    game.init_game()
    while not game.is_over():
        actions = game.get_legal_actions()
        #print(actions)
        action = np.random.choice(actions)
        state, _ = game.step(action)

    payoffs = game.get_payoffs()

    total = 0
    for payoff in payoffs:
        total += payoff
    assert total == 0