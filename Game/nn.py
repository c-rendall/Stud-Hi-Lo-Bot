import torch
import torch.nn as nn
import torch.nn.functional as F

class CardEmbedding(nn.Module):
    def __init__(self, dim):
        super(CardEmbedding, self).__init__()
        self.rank = nn.Embedding(13, dim)  # 13 ranks
        self.suit = nn.Embedding(4, dim)  # 4 suits
        self.card = nn.Embedding(52, dim)  # 52 unique cards

    def forward(self, input):
        B, num_cards = input.shape
        x = input.view(-1)
        valid = x.ge(0).float()  # -1 means "no card"
        x = x.clamp(min=0)  # Clamp to handle invalid cards
        embs = self.card(x) + self.rank(x // 4) + self.suit(x % 4)
        embs = embs * valid.unsqueeze(1)  # Zero out embeddings for "no cards"
        return embs.view(B, num_cards, -1).sum(1)

class DeepCFRModel(nn.Module):
    def __init__(self, n_card_types, n_bets, n_actions, dim=256):
        super(DeepCFRModel, self).__init__()
        self.card_embeddings = nn.ModuleList(
            [CardEmbedding(dim) for _ in range(n_card_types)]
        )
        self.card1 = nn.Linear(dim * n_card_types, dim)
        self.card2 = nn.Linear(dim, dim)
        self.card3 = nn.Linear(dim, dim)
        self.bet1 = nn.Linear(n_bets * 2, dim)
        self.bet2 = nn.Linear(dim, dim)
        self.comb1 = nn.Linear(2 * dim, dim)
        self.comb2 = nn.Linear(dim, dim)
        self.comb3 = nn.Linear(dim, dim)
        self.action_head = nn.Linear(dim, n_actions)

    def forward(self, cards, bets):
        # Card embeddings branch
        card_embs = [embedding(card_group) for embedding, card_group in zip(self.card_embeddings, cards)]
        card_embs = torch.cat(card_embs, dim=1)
        x = F.relu(self.card1(card_embs))
        x = F.relu(self.card2(x))
        x = F.relu(self.card3(x))

        # Bet embeddings branch
        bet_size = bets.clamp(0, 1e6)
        bet_occurred = bets.ge(0)
        bet_feats = torch.cat([bet_size, bet_occurred.float()], dim=1)
        y = F.relu(self.bet1(bet_feats))
        y = F.relu(self.bet2(y) + y)

        # Combined branch
        z = torch.cat([x, y], dim=1)
        z = F.relu(self.comb1(z))
        z = F.relu(self.comb2(z) + z)
        z = F.relu(self.comb3(z) + z)
        return self.action_head(z)