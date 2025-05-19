from django.shortcuts import render, redirect, get_object_or_404
from ..models import GameSession, Deck, Card, CardInHand, HandHistory, Hand
from ..constants.constants import GAME_ID, HAND_ID, HAND_IDS, HAND_INDEX
from ..utils import calculate_hand_value

import math

# Start a new game
def seat_selection(request):
    return render(request, 'game/seat_selection.html')