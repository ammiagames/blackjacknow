from .service.start_hand import start_hand
from .service.reset_chip_stack import reset_chip_stack
from .service.play_hand import play_hand
from django.views.decorators.http import require_POST
from .service.actions import double, split, insurance, even_money, hit, stand, join_seat

# Start a new game
def start_hand_view(request):
    return start_hand(request)

def reset_chips_view(request):
    return reset_chip_stack(request)

# Game display view
def play_hand_view(request):
    return play_hand(request)

def double_view(request):
    return double(request)

def split_view(request):
    return split(request)

def insurance_view(request):
    return insurance(request)

def even_money_view(request):
    return even_money(request)

# Handle player hit
def hit_view(request):
    return hit(request)

# Handle player stand
def stand_view(request):
    return stand(request)

@require_POST
def join_seat_view(request):
    return join_seat(request)
