import random 
import eval7 

class Deck: 
    def __init__(self): 
        '''
        Initializes a full deck of cards using eval7 and shuffles it
        '''
        self.cards = list(eval7.Deck()) # Creates a deck object
        self.shuffle()  # Shuffles the deck upon ititialization 

    def shuffle(self): 
        '''
        Shuffles the deck in place 
        '''
        random.shuffle(self.cards)

    def deal(self, num_cards=1): 
        '''
        Deals the top card from the deck.
        Returns: 
            - eval7.Card: the top card
        '''
        if num_cards > len(self.cards): 
            raise ValueError('Not enough cards left in the deck to deal.')
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:] # Remove the dealt cards from the deck 
        return dealt_cards 
    
    def remaining_cards(self): 
        '''
        Returns the number of cards left in the deck 
        '''
        return len(self.cards)