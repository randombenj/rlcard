import numpy as np
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.jass.utils import ACTION_LIST

from rlcard.agents.human_agents.jass_human_agent import HumanAgent

env = rlcard.make('jass')
env.set_agents([
    RandomAgent(env.num_actions),
    HumanAgent(env.num_actions),
    RandomAgent(env.num_actions),
    RandomAgent(env.num_actions)
])
env.reset()

trajectory, payoffs = env.run(is_training=False)

print(trajectory, payoffs)