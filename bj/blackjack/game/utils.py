import random

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
