from rlcard.games.jass.utils import get_legal_actions
from rlcard.games.base import Card

print(get_legal_actions([Card(suit='D', rank='6'), Card(suit='H', rank='8')], "D", [Card(suit='C', rank='7'), Card(suit='D', rank='Q')]))
