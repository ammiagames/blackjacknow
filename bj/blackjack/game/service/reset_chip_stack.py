from django.shortcuts import redirect
from ..models import GameSession
from ..constants.constants import GAME_ID
from ..service.start_hand import start_hand

def reset_chip_stack(request):
    if GAME_ID in request.session:
        game = GameSession.objects.get(id=request.session[GAME_ID])
        game.chip_count = 1000
        game.save()
    return redirect('game:start_hand')