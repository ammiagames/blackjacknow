from django.shortcuts import render, redirect, get_object_or_404
from ..models import GameSession, Deck, Card, CardInHand, HandHistory, Hand
from ..constants.constants import GAME_ID, HAND_ID, HAND_IDS, HAND_INDEX
from ..utils import calculate_hand_value

import math

# Start a new game
def start_hand(request):
    bet = int(request.POST.get('bet', 0))
    starting_chips = int(request.POST.get('chips', 1000))

    # Create/reset deck
    deck = Deck.objects.create()
    deck.reset_deck()

    # Get or create GameSession
    game = None
    if GAME_ID in request.session:
        game = get_object_or_404(GameSession, id=request.session[GAME_ID])
        if game.chip_count < bet:
            return render(request, 'game/start_hand.html', {
                'error': 'Not enough chips to place that bet.',
                'game': game
            })
        game.is_active = True
        game.chip_count -= bet
    else:
        game = GameSession.objects.create(chip_count=starting_chips - bet, deck=deck)

    # Create Hand object
    hand = Hand.objects.create(
        game_session=game,
        bet_amount=bet,
        is_current=True  # for tracking current hand if split logic is added later
    )
    # Draw initial cards
    player_card1, player_card2 = deck.draw_card(), deck.draw_card()
    dealer_card1, dealer_card2 = deck.draw_card(), deck.draw_card()
    # Save cards to CardInHand
    CardInHand.objects.bulk_create([
        CardInHand(hand=hand, card=player_card1, position=0, is_player=True),
        CardInHand(hand=hand, card=player_card2, position=1, is_player=True),
        CardInHand(hand=hand, card=dealer_card1, position=0, is_player=False),
        CardInHand(hand=hand, card=dealer_card2, position=1, is_player=False),
    ])

    # Calculate hand values
    player_cards = [player_card1, player_card2]
    dealer_cards = [dealer_card1, dealer_card2]
    player_value = calculate_hand_value(player_cards)
    dealer_value = calculate_hand_value(dealer_cards)

    # Set session context
    request.session[GAME_ID] = game.id
    request.session[HAND_INDEX] = 0
    request.session[HAND_IDS] = [hand.id]
    request.session['selected_seat'] = request.POST.get('seat')
    request.session['offer_even_money'] = False
    request.session['offer_insurance'] = False
    request.session['starting_chip_stack'] = game.chip_count

    # Offer insurance / even money logic
    if dealer_card1.rank == 'A':
        if player_value == 21:
            request.session['offer_even_money'] = True
        else:
            request.session['offer_insurance'] = True
    elif dealer_card1.rank in ['J', 'Q', 'K', 'T'] and dealer_card2.rank == 'A':
        game.is_active = False
        if player_value == 21:
            hand.result = "Dealer and player have blackjack. Push."
            game.chip_count += bet
        else:
            hand.result = "Dealer has blackjack"
    else:
        if player_value == 21:
            hand.result = "Congrats! You have Blackjack!"
            game.chip_count += math.floor(bet * 2.5)
            game.is_active = False
    hand.save()
    game.save()
    return redirect('game:play_hand')

    # # GET request — show start screen
    # game = None
    # if GAME_ID in request.session:
    #     try:
    #         game = GameSession.objects.get(id=request.session[GAME_ID])
    #         game.deck.reset_deck()
    #         game.save()
    #     except GameSession.DoesNotExist:
    #         pass

    # return render(request, 'game/start_hand.html', {'game': game})
