from django.test import TestCase
from game import utils
from game.models import Card, Hand, CardInHand, GameSession, Deck


class UtilsWithModelsTestCase(TestCase):

    def test_hand_value_17(self):
        cards = self.create_cards(['A', '6'])
        value = utils.calculate_hand_value(cards)
        self.assertEqual(value, 17)

    def test_hand_value_with_ace(self):
        cards = self.create_cards(['T', '8'])
        value = utils.calculate_hand_value(cards)
        self.assertEqual(value, 18)

    def test_can_split_true(self):
        cards = self.create_cards(['8', '8'])
        result = utils.can_split_hand(cards)
        self.assertTrue(result)

    def test_can_split_false(self):
        cards = self.create_cards(['8', '9'])
        result = utils.can_split_hand(cards)
        self.assertFalse(result)

    def test_can_split_invalid_card_count(self):
        cards = self.create_cards(['8'])
        result = utils.can_split_hand(cards)
        self.assertFalse(result)

    def create_cards(self, ranks):
        cards = []
        # Add cards to hand
        for rank in ranks:
            card = Card.objects.create(suit='h', rank=rank)
            cards.append(card)

        return cards
