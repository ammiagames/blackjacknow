function calculateCardValue(rank) {
    if (["J", "Q", "K", "T"].includes(rank)) return 10;
    if (rank === "A") return 11;
    return parseInt(rank);
}

document.addEventListener('DOMContentLoaded', () => {
    const dealerCards = document.querySelectorAll('#dealer-hand .card');
    const dealerTotalEl = document.getElementById('dealer-total');
    let total = 0;
    let aces = 0;

    dealerCards.forEach((card, index) => {
        if (card.textContent.includes('?')) return;

        setTimeout(() => {
            const rank = card.querySelector('.top-left')?.textContent.trim().charAt(0);
            if (!rank) return;

            total += calculateCardValue(rank);
            if (rank === 'A') aces++;

            while (total > 21 && aces > 0) {
                total -= 10;
                aces--;
            }

            card.classList.remove('hidden');
            dealerTotalEl.textContent = `Dealer Total: ${total}`;

            // Show results after the last card is revealed
            if (index === dealerCards.length - 1) {
                document.getElementById('game-result').style.display = 'block';
                document.querySelectorAll('.hand-result').forEach(el => {
                    el.style.display = 'block';
                });
            }
        }, index * 400); // Animate with a delay between cards
    });
});
