import torch
from regret import CFR
from state import GameState
from nn import DeepCFRModel
from game import Game
from player import Player
from deck import Deck

class Trainer:
    def __init__(self, game, cfr, model, optimizer, iterations, batch_size, device="cpu"):
        """
        Initialize the Trainer.

        Parameters:
        game (Game): The game instance (manages players, deck, and gameplay).
        cfr (CFR): The CFR instance for strategy updates.
        model (DeepCFRModel): The neural network model for approximating strategies.
        optimizer (torch.optim.Optimizer): Optimizer for training the neural network.
        iterations (int): Number of training iterations.
        batch_size (int): Batch size for training the neural network.
        device (str): Device to run training on ('cpu' or 'cuda').
        """
        self.game = game
        self.cfr = cfr
        self.model = model
        self.optimizer = optimizer
        self.iterations = iterations
        self.batch_size = batch_size
        self.device = device

    def simulate_game(self):
        """
        Simulate a single game to generate training data.
        
        Returns:
        list: A list of (state, action, reward) tuples collected during the game.
        """
        training_data = []
        state = self.game.initial_state()
        while not state.is_terminal():
            # Get the current information set and strategy
            info_set = state.get_information_set(state.to_move)
            strategy = self.cfr._regret_matching(info_set)

            # Sample an action based on the strategy
            actions = list(state.actions)
            action = random.choices(actions, weights=[strategy[a] for a in actions])[0]

            # Transition to the next state and calculate utility
            new_state = state.play(action)
            reward = new_state.evaluation() if new_state.is_terminal() else 0

            # Record the data for training
            training_data.append((info_set.abstract_state(), action, reward))

            # Move to the next state
            state = new_state

        return training_data

    def train_neural_network(self, training_data):
        """
        Train the neural network with the collected data.

        Parameters:
        training_data (list): A list of (state, action, reward) tuples.
        """
        self.model.train()
        states, actions, rewards = zip(*training_data)

        # Convert data to tensors
        states_tensor = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions_tensor = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32, device=self.device)

        # Forward pass through the network
        logits = self.model(states_tensor)
        loss = torch.nn.functional.cross_entropy(logits, actions_tensor, reduction="none")
        weighted_loss = (loss * rewards_tensor).mean()

        # Backpropagation
        self.optimizer.zero_grad()
        weighted_loss.backward()
        self.optimizer.step()

    def run(self):
        """
        Run the training loop.
        """
        for iteration in range(self.iterations):
            # Generate training data through self-play
            training_data = []
            for _ in range(self.batch_size):
                training_data += self.simulate_game()

            # Train the neural network with the collected data
            self.train_neural_network(training_data)

            # Update CFR regrets and strategies
            for info_set, regrets in self.cfr.regrets.items():
                strategy = self.cfr._regret_matching(info_set)
                self.cfr.strategy_sum[info_set] = {a: self.cfr.strategy_sum.get(info_set, {}).get(a, 0) + strategy[a]
                                                   for a in strategy}

            # Log progress
            if iteration % 100 == 0:
                print(f"Iteration {iteration}/{self.iterations} completed.")

        # Compute final Nash equilibrium strategies
        self.cfr.compute_nash_equilibrium()
        print("Training completed. Nash equilibrium strategies computed.")