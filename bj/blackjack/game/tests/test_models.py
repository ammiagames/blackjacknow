from django.test import TestCase
from game.models import Card, Deck
from game.models import DeckCard  # Assuming there's a through model for deck_cards

class CardModelTest(TestCase):
    def test_card_creation_and_str(self):
        card = Card.objects.create(suit='h', rank='A')
        self.assertEqual(str(card), 'Ah')

class DeckModelTest(TestCase):
    def setUp(self):
        self.deck = Deck.objects.create()
        self.deck.reset_deck()

    def test_reset_deck_creates_52_cards(self):
        self.assertEqual(self.deck.deck_cards.count(), 52)

    def test_draw_card_removes_card(self):
        count_before = self.deck.deck_cards.count()
        card = self.deck.draw_card()
        count_after = self.deck.deck_cards.count()
        self.assertIsNotNone(card)
        self.assertEqual(count_after, count_before - 1)

    def test_shuffle_changes_order(self):
        original_order = list(self.deck.deck_cards.values_list('card_id', flat=True))
        self.deck.shuffle()
        shuffled_order = list(self.deck.deck_cards.values_list('card_id', flat=True))
        self.assertNotEqual(original_order, shuffled_order)
