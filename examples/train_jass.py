import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.utils import tournament
from rlcard.utils import Logger



def main():
    # Make environment
    env = rlcard.make('jass', config={'seed': 0, 'env_num': 4})
    eval_env = rlcard.make('jass', config={'seed': 0, 'env_num': 4})

    # Set the iterations numbers and how frequently we evaluate performance
    evaluate_every = 100
    evaluate_num = 10000
    iteration_num = 5000

    # The intial memory size
    memory_init_size = 100

    # Train the agent every X steps
    train_every = 1

    # The paths for saving the logs and learning curves
    log_dir = './experiments/blackjack_dqn_result/'

    # Set a global seed
    #set_global_seed(0)


    with tf.Session() as sess:

            # Initialize a global step
            global_step = tf.Variable(0, name='global_step', trainable=False)

            # Set up the agents
            agent = DQNAgent(sess,
                            scope='dqn',
                            action_num=env.action_num,
                            replay_memory_init_size=memory_init_size,
                            train_every=train_every,
                            state_shape=env.state_shape,
                            mlp_layers=[10,10])
            env.set_agents([agent])
            eval_env.set_agents([agent])

            # Initialize global variables
            sess.run(tf.global_variables_initializer())

            # Initialize a Logger to plot the learning curve
            logger = Logger(log_dir)

            for iteration in range(iteration_num):

                # Generate data from the environment
                trajectories, _ = env.run(is_training=True)

                # Feed transitions into agent memory, and train the agent
                for ts in trajectories[0]:
                    agent.feed(ts)

                # Evaluate the performance. Play with random agents.
                if iteration % evaluate_every == 0:
                    logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])
            
            # Save model
            save_dir = 'models/blackjack_dqn'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            saver = tf.train.Saver()
            saver.save(sess, os.path.join(save_dir, 'model'))

if __name__ == '__main__':
    main()