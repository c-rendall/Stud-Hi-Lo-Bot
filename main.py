from game import Game
from player import Player
from deck import Deck
from regret import CFR
from trainer import Trainer
from nn import DeepCFRModel
import torch


def main():
    # Initialize the deck and players
    deck = Deck()
    players = [
        Player(name=f"Player {i+1}", chips=1000, model=None) for i in range(2)
    ]

    # Initialize the game
    ante = 5
    small_bet = 10
    big_bet = 20
    game = Game(players, ante, small_bet, big_bet, logger=None)

    # Initialize CFR and Neural Network components
    cfr_iterations = 10000
    cfr = CFR(game=game, iterations=cfr_iterations)

    n_card_types = 2  # Example: player and visible cards
    n_bets = 3  # Current bet, pot, and chips
    n_actions = 3  # Actions: fold, call, raise
    nn_dim = 256  # Size of neural network hidden layers
    model = DeepCFRModel(n_card_types=n_card_types, n_bets=n_bets, n_actions=n_actions, dim=nn_dim)

    # Configure optimizer and trainer
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    training_iterations = 1000
    batch_size = 10
    trainer = Trainer(game, cfr, model, optimizer, training_iterations, batch_size)

    # Run the training process
    print("Starting training...")
    trainer.run()

    # Output Nash equilibrium strategies
    print("Training complete. Nash equilibrium strategies:")
    for info_set, strategy in cfr.nash_equilibrium.items():
        print(f"Information Set: {info_set}, Strategy: {strategy}")

    # Optionally, simulate a game with trained strategies
    print("Simulating a game with trained strategies...")
    game.play_hand()


if __name__ == "__main__":
    main()