from Game.deck import Deck 
from Game.player import Player 
from Game.logging import GameLogger
import eval7

class Game:
    def __init__(self, players, ante, small_bet, big_bet, logger, bring_in=None):
        """
        Initialize the game with players, betting rules, and a shuffled deck.

        Parameters:
        players (list): List of Player objects.
        ante (int): The ante each player must pay at the start.
        small_bet (int): The bet amount for the first two betting rounds.
        big_bet (int): The bet amount for later rounds.
        logger (Logger): A logger object for tracking hand history.
        bring_in (int): The bring-in amount (optional, defaults to small_bet/2).
        """
        self.players = players
        self.ante = ante
        self.small_bet = small_bet
        self.big_bet = big_bet
        self.bring_in = bring_in if bring_in is not None else small_bet // 2
        self.pot = 0
        self.deck = Deck()
        self.logger = logger
        self.current_round = "third_street"  # Start at third street
        self.active_players = players.copy()  # Players still in the hand

    def ante_up(self):
        """
        Each player pays the ante, and it is added to the pot.
        """
        for player in self.players:
            player.chips -= self.ante
            self.pot += self.ante
            self.logger.info(f"{player.name} pays ante of {self.ante}. Chips left: {player.chips}")

    def deal_card(self):
        """
        Deal one card to each active player.
        """
        for player in self.active_players:
            card = self.deck.deal(1)[0]  # Deal one card
            player.hand.append(card)
            self.logger.info(f"{player.name} receives a card: {card}")

    def determine_bring_in(self):
        """
        Determine the bring-in player based on the lowest visible card.
        If multiple players have the same lowest card, use suit rankings.
        """
        lowest_card = None
        bring_in_player = None
        for player in self.active_players:
            visible_card = player.hand[2]  # Upcard is the third card dealt
            if not lowest_card or (
                visible_card < lowest_card or
                (visible_card == lowest_card and player < bring_in_player)
            ):
                lowest_card = visible_card
                bring_in_player = player
        return bring_in_player

    def betting_round(self, bet_limit):
        """
        Execute a betting round.
        Parameters:
        bet_limit (int): The maximum bet/raise for this round.
        """
        current_bet = 0
        action_done = [False] * len(self.active_players)

        while not all(action_done):
            for i, player in enumerate(self.active_players):
                if action_done[i]:
                    continue
                action = player.take_action(current_bet, bet_limit)
                if action == "fold":
                    self.logger.info(f"{player.name} folds.")
                    self.active_players.remove(player)
                elif action == "call":
                    call_amount = current_bet - player.current_bet
                    player.chips -= call_amount
                    self.pot += call_amount
                    player.current_bet += call_amount
                    self.logger.info(f"{player.name} calls {call_amount}. Chips left: {player.chips}")
                elif action == "raise":
                    raise_amount = bet_limit
                    current_bet += raise_amount
                    player.chips -= current_bet - player.current_bet
                    self.pot += current_bet - player.current_bet
                    player.current_bet = current_bet
                    action_done = [False] * len(self.active_players)  # Reset actions
                    self.logger.info(f"{player.name} raises to {current_bet}. Chips left: {player.chips}")
                action_done[i] = True

    def determine_highest_hand(self):
        """
        Determine the highest visible hand among the active players.
        This player will act first in the next betting round.
        """
        highest_hand = None
        acting_player = None
        for player in self.active_players:
            visible_hand = player.get_visible_hand()
            hand_rank = eval7.HandEvaluator.evaluate(visible_hand)
            if not highest_hand or hand_rank > highest_hand:
                highest_hand = hand_rank
                acting_player = player
        return acting_player

    def showdown(self):
        """
        Compare hands and determine the winner of the pot.
        """
        best_hand = None
        winner = None
        for player in self.active_players:
            hand_rank = eval7.HandEvaluator.evaluate(player.hand)
            if not best_hand or hand_rank > best_hand:
                best_hand = hand_rank
                winner = player
        winner.chips += self.pot
        self.logger.info(f"{winner.name} wins the pot of {self.pot} with {winner.hand}.")
        self.pot = 0

    def play_hand(self):
        """
        Play a single hand of Seven Card Stud Hi/Lo.
        """
        self.logger.info("New hand starting...")
        self.ante_up()
        self.deal_card()  # Deal initial cards (2 down, 1 up)
        self.deal_card()
        self.deal_card()
        bring_in_player = self.determine_bring_in()
        self.logger.info(f"{bring_in_player.name} is the bring-in player.")

        # Betting rounds
        for street in ["third_street", "fourth_street", "fifth_street", "sixth_street", "seventh_street"]:
            self.current_round = street
            self.betting_round(self.small_bet if street in ["third_street", "fourth_street"] else self.big_bet)
            if street != "seventh_street":
                self.deal_card()

        # Showdown
        if len(self.active_players) > 1:
            self.showdown()

