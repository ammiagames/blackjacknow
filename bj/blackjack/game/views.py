from django.shortcuts import render, redirect, get_object_or_404
from .models import GameSession, Deck, Card, CardInHand, HandHistory
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

# Start a new game
def start_game(request):
    if request.method == 'POST':
        bet = int(request.POST.get('bet', 0))

        # Create and reset deck
        deck = Deck.objects.create()
        deck.reset_deck()

        # Draw initial cards
        player_card1 = deck.draw_card()
        player_card2 = deck.draw_card()
        dealer_card1 = deck.draw_card()
        dealer_card2 = deck.draw_card()
        player_cards = [player_card1, player_card2]
        dealer_cards = [dealer_card1, dealer_card2]
        dealer_card1.rank = 'A'
        dealer_card1.save()
        dealer_card2.rank = 'T'
        dealer_card2.save()
        player_card1.rank = 'A'
        player_card1.save()
        player_card2.rank = 'T'
        player_card2.save()
        player_value = calculate_hand_value(player_cards)
        dealer_value = calculate_hand_value(dealer_cards)

        game = None
        if 'game_id' in request.session:
            game = GameSession.objects.get(id=request.session['game_id'])
            if game.chip_count < bet:
                return render(request, 'game/start_game.html', {
                    'error': 'Not enough chips to place that bet.',
                    'game': game
                })
            game.is_active=True
            game.bet_amount = bet
            game.chip_count -= bet
            game.save()
        else:
            # Create game session
            game = GameSession.objects.create(
                chip_count=1000 - bet,
                bet_amount=bet,
                deck=deck
            )
        hand_id = request.session.get('hand_id', 0) + 1
        request.session['hand_id'] = hand_id

        # Add cards to CardInHand
        CardInHand.objects.bulk_create([
            CardInHand(game_session=game, card=player_card1, is_player=True, position=hand_id),
            CardInHand(game_session=game, card=player_card2, is_player=True, position=hand_id),
            CardInHand(game_session=game, card=dealer_card1, is_player=False, position=hand_id),
            CardInHand(game_session=game, card=dealer_card2, is_player=False, position=hand_id),
        ])

        # Insurance and even money offer
        request.session['offer_even_money'] = False
        request.session['offer_insurance'] = False
        if dealer_card1.rank == 'A':
            if player_value == 21:
                request.session['offer_even_money'] = True
            else:
                request.session['offer_insurance'] = True
        
        # 10 blackjack path
        if dealer_card1.rank in ['J', 'Q', 'K', 'T'] and dealer_card2.rank == 'A':
            game.is_active = False
            if player_value == 21:
                game.result = "Dealer and player have blackjack. Push."
                game.chip_count += game.bet_amount
            else:
                game.result = "Dealer has blackjack"
            game.save()
            
        request.session['game_id'] = game.id
        return redirect('game:play_game')
    game = None
    if 'game_id' in request.session:
        try:
            game = GameSession.objects.get(id=request.session['game_id'])
            game.deck.reset_deck()
            game.save()
        except GameSession.DoesNotExist:
            pass

    return render(request, 'game/start_game.html', {'game': game})

def reset_chips(request):
    if 'game_id' in request.session:
        game = GameSession.objects.get(id=request.session['game_id'])
        game.chip_count = 1000
        game.save()
    return redirect('game:start_game')

# Utility: calculate hand value
def calculate_hand_value(cards):
    value = 0
    aces = 0
    for card in cards:
        rank = card.rank
        if rank in ['K', 'Q', 'J', 'T']:
            value += 10
        elif rank == 'A':
            value += 11
            aces += 1
        else:
            value += int(rank)

    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Game display view
def play_game(request):
    game_id = request.session.get('game_id')
    offer_insurance = request.session['offer_insurance']
    offer_even_money = request.session['offer_even_money']
    if not game_id:
        return redirect('game:start_game')
    hand_id = request.session['hand_id']

    game = get_object_or_404(GameSession, id=game_id)
    player_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=True, position=hand_id)]
    dealer_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id)]
    player_value = calculate_hand_value(player_cards)
    context = {
        'game': game,
        'player_cards': player_cards,
        'player_total': player_value,
        'dealer_cards': dealer_cards if not game.is_active else dealer_cards[:1],
        'hide_dealer_card': game.is_active,
        'offer_insurance': offer_insurance,
        'offer_even_money': offer_even_money
    }
    print("offer_even_money")
    print(offer_even_money)

    if offer_even_money:
        return render(request, 'game/play_game.html', context)
    
    # game.save()
    return render(request, 'game/play_game.html', context)

def insurance(request):
    game_id = request.session.get('game_id')
    request.session['offer_insurance'] = False
    game = get_object_or_404(GameSession, id=game_id)
    hand_id = request.session['hand_id']

    choice = request.POST.get('insurance_choice')
    dealer_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id).order_by('id')]
    hidden_card = dealer_cards[1]
    if "yes" == choice:
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            game.result = "Dealer has blackjack: Insurance wins."
            game.chip_count += (game.bet_amount)
            game.is_active = False
        else:
            game.chip_count -= (game.bet_amount / 2)
            messages.info(request, "Insurance lost. No one's home.")
    else:
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            game.result = "Dealer has blackjack"
            game.is_active = False
        else:
            messages.info(request, "Insurance not taken. No one's home.")
    game.save()
    return redirect('game:play_game')

def even_money(request):
    game_id = request.session.get('game_id')
    request.session['offer_even_money'] = False
    game = get_object_or_404(GameSession, id=game_id)
    hand_id = request.session['hand_id']

    choice = request.POST.get('even_money_choice')
    dealer_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id).order_by('id')]
    hidden_card = dealer_cards[1]
    game.is_active = False
    if "yes" == choice:
        game.chip_count += (game.bet_amount * 2)
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            game.result = "Even money taken; Dealer had Blackjack"
            game.is_active = False
        else:
            game.result = "Even money taken; no one was home"
    else:
        if hidden_card.rank in ['J', 'Q', 'K', 'T']:
            game.result = "Dealer has blackjack. Push."
            game.chip_count += (game.bet_amount)
            game.is_active = False
        else:
            messages.info(request, "Even money not taken. No one's home.")
    game.save()
    return redirect('game:play_game')

# Handle player hit
def hit(request):
    game_id = request.session.get('game_id')
    game = get_object_or_404(GameSession, id=game_id)
    hand_id = request.session['hand_id']

    new_card = game.deck.draw_card()
    CardInHand.objects.create(game_session=game, card=new_card, is_player=True, position=hand_id)

    # Check for bust
    player_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=True, position=hand_id)]
    dealer_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id)]
    player_value = calculate_hand_value(player_cards)
    dealer_value = calculate_hand_value(dealer_cards)
    if player_value > 21:
        game.is_active = False
        game.result = 'Player Busts! Dealer Wins.'
        game.save()

        HandHistory.objects.create(
            game_session=game,
            hand_id=hand_id,
            player_total=player_value,
            dealer_total=dealer_value,
            result=game.result,
            bet_amount=game.bet_amount,
            chip_count_after=game.chip_count
        )
    elif player_value == 21:
        return redirect('game:stand')

    return redirect('game:play_game')

# Handle player stand
def stand(request):
    game_id = request.session.get('game_id')
    game = get_object_or_404(GameSession, id=game_id)
    hand_id = request.session['hand_id']

    # Dealer plays
    while True:
        dealer_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id)]
        dealer_value = calculate_hand_value(dealer_cards)

        if dealer_value >= 17:
            break

        new_card = game.deck.draw_card()
        if not new_card:
            break
        CardInHand.objects.create(game_session=game, card=new_card, is_player=False, position=hand_id)

    # Final hand values
    player_cards = [cih.card for cih in game.cardinhand_set.filter(is_player=True, position=hand_id)]
    player_value = calculate_hand_value(player_cards)
    dealer_value = calculate_hand_value([cih.card for cih in game.cardinhand_set.filter(is_player=False, position=hand_id)])

    # Determine outcome
    if dealer_value > 21 or player_value > dealer_value:
        game.result = 'Player Wins!'
        game.chip_count += game.bet_amount * 2
    elif player_value == dealer_value:
        game.result = 'Push (Tie)'
        game.chip_count += game.bet_amount
    else:
        game.result = 'Dealer Wins.'

    game.is_active = False
    game.save()

    HandHistory.objects.create(
        game_session=game,
        hand_id=hand_id,
        player_total=player_value,
        dealer_total=dealer_value,
        result=game.result,
        bet_amount=game.bet_amount,
        chip_count_after=game.chip_count
    )

    return redirect('game:play_game')
