import logging
from Game import game
from deck import Deck
from player import Player
from logging import GameLogger

# Mock Player class for testing
class MockPlayer:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0

    def take_action(self, current_bet, bet_limit):
        """
        Simulate player actions for testing.
        Players will call if they can afford it, or fold if not.
        """
        if self.chips >= (current_bet - self.current_bet):
            return "call"
        return "fold"

    def get_visible_hand(self):
        """
        Return all the upcards for hand evaluation.
        For simplicity in testing, assume all cards are upcards.
        """
        return self.hand

# Set up a logger for testing
def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("GameTestLogger")
    return logger

# Test the Game class
def test_game():
    # Initialize logger
    logger = setup_logger()

    # Create mock players
    players = [
        MockPlayer("Alice", 100),
        MockPlayer("Bob", 100),
        MockPlayer("Charlie", 100)
    ]

    # Initialize the game
    ante = 5
    small_bet = 10
    big_bet = 20
    game_logger = GameLogger("test_game.log")
    game = Game(players, ante, small_bet, big_bet, game_logger)

    # Play a hand
    game.play_hand()

# Run the test script
if __name__ == "__main__":
    test_game()
