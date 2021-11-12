import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.jass.utils import ACTION_LIST
from .determism_util import is_deterministic




def test_reset_and_extract_state():
    env = rlcard.make('jass')
    state, _ = env.reset()
    assert state['obs'].size, 240


def test_is_deterministic():
    assert is_deterministic('jass')



def test_get_legal_actions():
    env = rlcard.make('jass')
    env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
    env.reset()
    legal_actions = env._get_legal_actions()
    for legal_action in legal_actions:
        assert legal_action < 36


def test_step():
    env = rlcard.make('jass')
    state, _ = env.reset()
    action = np.random.choice(list(state['legal_actions'].keys()))
    _, player_id = env.step(action)
    assert player_id == env.game.round.current_player

# don't know if needed ...
#def test_step_back():
#    env = rlcard.make('jass', config={'allow_step_back':True})
#    state, player_id = env.reset()
#    action = np.random.choice(list(state['legal_actions'].keys()))
#    env.step(action)
#    env.step_back()
#    self.assertEqual(env.game.round.current_player, player_id)
#
#    env = rlcard.make('jass', config={'allow_step_back':False})
#    state, player_id = env.reset()
#    action = np.random.choice(list(state['legal_actions'].keys()))
#    env.step(action)
#    # env.step_back()
#    assertException, env.step_back)



def test_run():
    env = rlcard.make('jass')
    env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
    trajectories, payoffs = env.run(is_training=False)
    assert len(trajectories) == 4
    total = 0
    for payoff in payoffs:
        total += payoff
    assert total == 0
    trajectories, payoffs = env.run(is_training=True)
    total = 0
    for payoff in payoffs:
        total += payoff
    assert total == 0



def test_decode_action():
    env = rlcard.make('jass')
    env.reset()
    legal_actions = env._get_legal_actions()
    for legal_action in legal_actions:
        decoded = env._decode_action(legal_action)
        assert decoded == ACTION_LIST[legal_action]

def test_get_perfect_information():
    env = rlcard.make('jass')
    _, player_id = env.reset()
    assert player_id == env.get_perfect_information()['current_player']

"""
"""