from django.shortcuts import render, redirect, get_object_or_404
from ..models import GameSession, Deck, Card, CardInHand, HandHistory, Hand
from ..constants.constants import GAME_ID, HAND_ID, HAND_IDS, HAND_INDEX
from ..utils import calculate_hand_value, can_split_hand

import math

def play_hand(request):
    game_id = request.session.get(GAME_ID)
    offer_insurance = request.session.get('offer_insurance', False)
    offer_even_money = request.session.get('offer_even_money', False)
    starting_chip_stack = request.session.get('starting_chip_stack', -1)

    if not game_id:
        return redirect('game:start_hand')

    hand_index = request.session[HAND_INDEX]
    hand_ids = request.session[HAND_IDS]

    game = get_object_or_404(GameSession, id=game_id)
    all_hands = Hand.objects.filter(id__in=hand_ids)
    first_hand = get_object_or_404(Hand, id=hand_ids[0])

    player_hands = []
    for hand in all_hands:
        cards = [cih.card for cih in hand.cards.filter(is_player=True).order_by('position')]
        can_split = can_split_hand(cards)
        player_hands.append({
            'hand_id': hand.id,
            'cards': cards,
            'value': calculate_hand_value(cards),
            'result': hand.result,
            'bet_amount': hand.bet_amount,
            'can_double': len(cards) == 2,
            'can_split': can_split
        })

    dealer_cards = [cih.card for cih in first_hand.cards.filter(is_player=False).order_by('position')]
    hand_id = 0
    active_hand = None
    player_cards = []
    if not hand_index >= len(hand_ids):
        hand_id = hand_ids[hand_index]
        active_hand = get_object_or_404(Hand, id=hand_id)
        player_cards = [cih.card for cih in active_hand.cards.filter(is_player=True).order_by('position')]

    context = {
        'game': game,
        'player_hands': player_hands,
        'active_hand': player_hands[hand_index] if hand_index < len(player_hands) else None,
        'dealer_cards': dealer_cards if not game.is_active else dealer_cards[:1],
        'hide_dealer_card': game.is_active,
        'offer_insurance': offer_insurance,
        'offer_even_money': offer_even_money,
        'starting_chip_stack': starting_chip_stack,
    }

    return render(request, 'game/play_hand.html', context)
