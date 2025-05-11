from django.shortcuts import render, redirect, get_object_or_404
from ..models import GameSession, Deck, Card, CardInHand, HandHistory, Hand
from ..constants.constants import GAME_ID, HAND_ID, HAND_IDS, HAND_INDEX
from ..utils import calculate_hand_value
from django.db import transaction
from django.contrib import messages

import math

def insurance(request):
    game_id = request.session.get(GAME_ID)
    hand_id = request.session.get(HAND_IDS)[request.session.get(HAND_INDEX)]
    request.session['offer_insurance'] = False

    game = get_object_or_404(GameSession, id=game_id)
    hand = get_object_or_404(Hand, id=hand_id, game_session=game)

    choice = request.POST.get('insurance_choice')
    dealer_cards = [cih.card for cih in hand.cards.filter(is_player=False).order_by('position')]
    hidden_card = dealer_cards[1]

    if choice == "yes":
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            hand.result = "Dealer has blackjack: Insurance wins."
            game.chip_count += hand.bet_amount
            hand.is_current = False
            game.is_active = False
        else:
            game.chip_count -= (hand.bet_amount / 2)
            messages.info(request, "Insurance lost. No one's home.")
    else:
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            hand.result = "Dealer has blackjack."
            hand.is_current = False
            game.is_active = False
        else:
            messages.info(request, "Insurance not taken. No one's home.")

    game.save()
    hand.save()
    return redirect('game:play_hand')

def even_money(request):
    game_id = request.session.get(GAME_ID)
    hand_index = request.session.get(HAND_INDEX)
    hand_id = request.session.get(HAND_IDS)[hand_index]
    request.session['offer_even_money'] = False

    game = get_object_or_404(GameSession, id=game_id)
    hand = get_object_or_404(Hand, id=hand_id, game_session=game)

    choice = request.POST.get('even_money_choice')
    dealer_cards = [cih.card for cih in hand.cards.filter(is_player=False).order_by('position')]
    hidden_card = dealer_cards[1]

    hand.is_current = False
    game.is_active = False

    if choice == "yes":
        game.chip_count += (hand.bet_amount * 2)
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            hand.result = "Even money taken; Dealer had Blackjack"
        else:
            hand.result = "Even money taken; no one was home"
    else:
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            hand.result = "Dealer has blackjack. Push."
            game.chip_count += hand.bet_amount
        else:
            hand.result = "No one's home!"
            game.chip_count += math.floor(hand.bet_amount * 2.5)

    game.save()
    hand.save()
    return redirect('game:play_hand')

def hit(request):
    game_id = request.session.get(GAME_ID)
    game = get_object_or_404(GameSession, id=game_id)
    hands = request.session[HAND_IDS]
    hand_id = hands[request.session[HAND_INDEX]]

    # Get the current hand associated with the hand_id
    hand = get_object_or_404(Hand, id=hand_id, game_session=game)

    # Draw a new card from the deck
    new_card = game.deck.draw_card()

    # Add the new card to the hand
    CardInHand.objects.create(hand=hand, card=new_card, position=hand.cards.count(), is_player=True)

    # Calculate the player and dealer values for this hand
    player_cards = [cih.card for cih in hand.cards.filter(is_player=True).order_by('position')]
    dealer_cards = [cih.card for cih in hand.cards.filter(is_player=False).order_by('position')]
    player_value = calculate_hand_value(player_cards)
    dealer_value = calculate_hand_value(dealer_cards)

    # Check if the player busts
    if player_value > 21:
        request.session[HAND_INDEX] += 1
        if request.session[HAND_INDEX] >= len(hands):
            set_hand_results(hands, dealer_value, game)
        else:
            hand.result = 'Player Busts! Dealer Wins.'
            hand.save()

    return redirect('game:play_hand')

def stand(request):
    game_id = request.session.get(GAME_ID)
    game = get_object_or_404(GameSession, id=game_id)
    hand_index = request.session[HAND_INDEX]
    hands = request.session[HAND_IDS]

    hand_index += 1
    if hand_index >= len(hands):
        first_hand = get_object_or_404(Hand, id=hands[0], game_session=game)
        # Dealer plays
        dealer_cards = [cih.card for cih in first_hand.cards.filter(is_player=False).order_by('position')]
        dealer_value = -1
        while True:
            dealer_value = calculate_hand_value(dealer_cards)
            if dealer_value >= 17:
                break

            new_card = game.deck.draw_card()
            if not new_card:
                break
            new_cih = CardInHand.objects.create(
                hand=first_hand,
                card=new_card,
                is_player=False,
                position=first_hand.cards.filter(is_player=False).count()
            )
            dealer_cards.append(new_card)

        set_hand_results(hands, dealer_value, game)
    else:
        request.session[HAND_INDEX] = hand_index

    return redirect('game:play_hand')

def double(request):
    game_id = request.session.get(GAME_ID)
    hands = request.session[HAND_IDS]
    hand_id = hands[request.session[HAND_INDEX]]
    game = get_object_or_404(GameSession, id=game_id)
    hand = get_object_or_404(Hand, id=hand_id, game_session=game)

    player_cards = [cih.card for cih in hand.cards.filter(is_player=True).order_by('position')]

    # Validate double down conditions

    # TODO: this is tripped up even when there ar eonly two cards
    if len(player_cards) != 2:
        messages.error(request, "Double down is only allowed with exactly two cards.")
        return redirect('game:play_hand')

    if game.chip_count < hand.bet_amount:
        messages.error(request, "Not enough chips to double down.")
        return redirect('game:play_hand')

    with transaction.atomic():
        # Deduct and double bet
        game.chip_count -= hand.bet_amount
        hand.bet_amount *= 2
        game.save()
        hand.save()

        # Draw one card for the player
        new_card = game.deck.draw_card()
        CardInHand.objects.create(
            hand=hand,
            card=new_card,
            is_player=True,
            position=hand.cards.filter(is_player=True).count()
        )

    return redirect('game:stand')  # Auto-stand after doubling

def split(request):
    game_id = request.session.get(GAME_ID)
    hands = request.session[HAND_IDS]
    hand_id = hands[request.session[HAND_INDEX]]
    game = get_object_or_404(GameSession, id=game_id)
    original_hand = get_object_or_404(Hand, id=hand_id, game_session=game)

    player_cards = list(original_hand.cards.filter(is_player=True).order_by('position'))

    # Validate split conditions
    if len(player_cards) != 2 or player_cards[0].card.rank != player_cards[1].card.rank:
        messages.error(request, "You can only split with two cards of the same rank.")
        return redirect('game:play_hand')
    elif game.chip_count < original_hand.bet_amount:
        messages.error(request, "Not enough chips to split.")
        return redirect('game:play_hand')

    with transaction.atomic():
        # Deduct additional bet and create new split hand
        game.chip_count -= original_hand.bet_amount
        game.save()

        new_hand = Hand.objects.create(
            game_session=game,
            bet_amount=original_hand.bet_amount,
            is_current=False
        )

        # Move one card to new hand
        card_to_move = player_cards[1]
        card_to_move.hand = new_hand
        card_to_move.position = 0
        card_to_move.save()

        # Redraw one card for each hand
        card1 = game.deck.draw_card()
        card2 = game.deck.draw_card()

        CardInHand.objects.create(hand=original_hand, card=card1, is_player=True, position=1)
        CardInHand.objects.create(hand=new_hand, card=card2, is_player=True, position=1)

        # Track both hands in session for split flow
        hands.append(new_hand.id)
        request.session[HAND_IDS] = hands

        if player_cards[0].card.rank == 'A' == player_cards[1].card.rank:
            request.session[HAND_INDEX] = hand_id + 2
            return redirect('game:stand')

    return redirect('game:play_hand')

def set_hand_results(hands, dealer_value, game):
    game.is_active = False
    for hand_id in hands:
        hand = get_object_or_404(Hand, id=hand_id)

        # Final hand values
        player_cards = [cih.card for cih in hand.cards.filter(is_player=True).order_by('position')]
        player_value = calculate_hand_value(player_cards)

        # Determine outcome
        if player_value > 21:
            hand.result = 'Player Bust!'
        elif dealer_value > 21 or player_value > dealer_value:
            hand.result = 'Player Wins!'
            game.chip_count += hand.bet_amount * 2
        elif player_value == dealer_value:
            hand.result = 'Push (Tie)'
            game.chip_count += hand.bet_amount
        else:
            hand.result = 'Dealer Wins.'

        hand.is_current = False
        hand.save()

        # Save hand history
        HandHistory.objects.create(
            game_session=game,
            hand_id=hand.id,
            player_total=player_value,
            dealer_total=dealer_value,
            result=hand.result,
            bet_amount=hand.bet_amount,
            chip_count_after=game.chip_count
        )
    game.save()
    