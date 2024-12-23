import eval7

class GameState:
    def __init__(self, players, pot=0, current_round="third_street"):
        """
        Initialize a GameState object.

        Parameters:
        players (list): List of Player objects participating in the game.
        pot (int): The current total pot size (default is 0).
        current_round (str): The current betting round (default is "third_street").
        """
        self.players = players
        self.pot = pot
        self.current_round = current_round
        self.action_history = []  # List of tuples (player, action, amount)
        self.visible_cards = {player.name: [] for player in players}  # Visible cards per player

    def reset(self):
        """
        Reset the game state for a new hand.
        """
        self.pot = 0
        self.current_round = "third_street"
        self.action_history = []
        self.visible_cards = {player.name: [] for player in self.players}

    def update_pot(self, amount):
        """
        Add an amount to the pot.

        Parameters:
        amount (int): The amount to add to the pot.
        """
        self.pot += amount

    def add_action(self, player, action, amount=0):
        """
        Record a player's action in the action history.

        Parameters:
        player (Player): The player performing the action.
        action (str): The action taken (e.g., "fold", "call", "raise").
        amount (int): The amount involved in the action (default is 0).
        """
        self.action_history.append((player.name, action, amount))

    def update_visible_cards(self, player, card):
        """
        Add a card to a player's visible cards.

        Parameters:
        player (Player): The player receiving the card.
        card (eval7.Card): The card to add to the visible cards.
        """
        self.visible_cards[player.name].append(card)

    def get_visible_hand(self, player):
        """
        Get the visible cards of a player.

        Parameters:
        player (Player): The player whose visible hand is requested.

        Returns:
        list: A list of eval7.Card objects representing the player's visible hand.
        """
        return self.visible_cards[player.name]

    def evaluate_visible_strength(self, player):
        """
        Evaluate the strength of a player's visible cards.

        Parameters:
        player (Player): The player whose visible hand strength is evaluated.

        Returns:
        float: The hand strength value (higher is better).
        """
        visible_hand = self.get_visible_hand(player)
        if len(visible_hand) < 2:
            return 0  # Not enough cards to evaluate
        return eval7.HandEvaluator.evaluate(visible_hand)

    def determine_next_actor(self):
        """
        Determine the next player to act based on visible hand strength.

        Returns:
        Player: The player with the strongest visible hand.
        """
        best_player = None
        best_strength = None
        for player in self.players:
            if player in self.visible_cards:
                strength = self.evaluate_visible_strength(player)
                if best_strength is None or strength > best_strength:
                    best_player = player
                    best_strength = strength
        return best_player

    def encode_state(self):
        """
        Encode the current game state for use by the neural network.

        Returns:
        dict: Encoded state information.
        """
        encoded_state = {
            "pot": self.pot,
            "current_round": self.current_round,
            "visible_cards": {player: [card.index for card in cards] for player, cards in self.visible_cards.items()},
            "action_history": self.action_history,
        }
        return encoded_state

    def next_round(self):
        """
        Transition to the next betting round.
        """
        rounds = ["third_street", "fourth_street", "fifth_street", "sixth_street", "seventh_street"]
        current_index = rounds.index(self.current_round)
        if current_index + 1 < len(rounds):
            self.current_round = rounds[current_index + 1]