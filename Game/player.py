import random
import torch

class Player:
    def __init__(self, name, chips, model, device="cpu"):
        """
        Initialize a Player object.

        Parameters:
        name (str): The player's name.
        chips (int): The player's starting chip stack.
        model (DeepCFRModel): A trained or untrained CFR neural network model.
        device (str): The device for model computations (e.g., 'cpu' or 'cuda').
        """
        self.name = name
        self.chips = chips
        self.hand = []  # Cards dealt to the player
        self.current_bet = 0
        self.action_history = []  # History of actions taken
        self.model = model  # The CFR neural network
        self.device = device

    def reset_for_new_hand(self):
        """
        Reset player state for a new hand.
        """
        self.hand = []
        self.current_bet = 0
        self.action_history = []

    def encode_state(self, current_bet, pot, visible_cards):
        """
        Encode the current game state into a format usable by the neural network.

        Parameters:
        current_bet (int): The current bet size in the round.
        pot (int): The total chips in the pot.
        visible_cards (list): The visible cards on the table.

        Returns:
        torch.Tensor: Encoded game state as a tensor.
        """
        # Example state encoding: visible cards, current bet, pot size, and player chips
        encoded_state = {
            "cards": torch.tensor([card.index for card in self.hand], dtype=torch.long, device=self.device),
            "visible_cards": torch.tensor([card.index for card in visible_cards], dtype=torch.long, device=self.device),
            "current_bet": torch.tensor([current_bet], dtype=torch.float32, device=self.device),
            "pot": torch.tensor([pot], dtype=torch.float32, device=self.device),
            "chips": torch.tensor([self.chips], dtype=torch.float32, device=self.device),
        }
        return encoded_state

    def take_action(self, current_bet, pot, visible_cards, legal_actions):
        """
        Determine the player's action based on the CFR neural network probabilities.

        Parameters:
        current_bet (int): The current bet size in the round.
        pot (int): The total chips in the pot.
        visible_cards (list): The visible cards on the table.
        legal_actions (list): Legal actions available to the player (e.g., ["fold", "call", "raise"]).

        Returns:
        str: The chosen action.
        """
        # Encode the game state
        state = self.encode_state(current_bet, pot, visible_cards)

        # Query the model for action probabilities
        with torch.no_grad():
            cards = torch.stack([state["cards"], state["visible_cards"]])
            bets = torch.cat([state["current_bet"], state["pot"], state["chips"]])
            logits = self.model(cards, bets)
            probabilities = torch.softmax(logits, dim=-1)

        # Filter probabilities for legal actions
        legal_indices = [legal_actions.index(action) for action in legal_actions]
        filtered_probs = probabilities[legal_indices]
        filtered_probs /= filtered_probs.sum()  # Normalize to 1

        # Sample an action based on the probabilities
        action = random.choices(legal_actions, weights=filtered_probs.tolist())[0]

        # Update action history
        self.action_history.append(action)
        return action

    def update_chips(self, amount):
        """
        Update the player's chip stack.

        Parameters:
        amount (int): The amount to add or subtract from the chip stack.
        """
        self.chips += amount

    def update_regrets(self, action, regret):
        """
        Update the player's regrets based on the chosen action.

        Parameters:
        action (str): The action taken.
        regret (float): The regret value to update.
        """
        # Placeholder for regret tracking; integrate with a regret table or external tracker
        pass