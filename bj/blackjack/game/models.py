from django.db import models
import random

class Card(models.Model):
    SUITS = ['h', 'd', 's', 'c']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    suit = models.CharField(max_length=1, choices=[(s, s) for s in SUITS])
    rank = models.CharField(max_length=2, choices=[(r, r) for r in RANKS])

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck(models.Model):
    def shuffle(self):
        cards = list(self.deck_cards.all())
        random.shuffle(cards)
        for i, deck_card in enumerate(cards):
            deck_card.position = i
            deck_card.save()

    def draw_card(self):
        top_card = self.deck_cards.first()
        if top_card:
            card = top_card.card
            top_card.delete()
            return card
        return None

    def reset_deck(self):
        self.deck_cards.all().delete()
        position = 0
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                card = Card.objects.create(suit=suit, rank=rank)
                DeckCard.objects.create(deck=self, card=card, position=position)
                position += 1
        self.shuffle()


class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='deck_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.card} (pos {self.position})"


class GameSession(models.Model):
    chip_count = models.IntegerField(default=1000)
    bet_amount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    result = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)


class CardInHand(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    is_player = models.BooleanField(default=False)
    position = models.IntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{'Player' if self.is_player else 'Dealer'}: {self.card}"

class HandHistory(models.Model):
    game_session = models.ForeignKey('GameSession', on_delete=models.CASCADE)
    hand_id = models.IntegerField()
    player_total = models.IntegerField()
    dealer_total = models.IntegerField()
    result = models.CharField(max_length=50)
    bet_amount = models.IntegerField()
    chip_count_after = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']