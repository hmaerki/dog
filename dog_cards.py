COLOURS = ('C', 'D', 'H', 'S')

LIST_4_COLOURS = (
    # https://docs.google.com/spreadsheets/d/1fnAL9Csg0xfkZqHPyxq1r5kL7MLX200DlCBzDXKeito/edit?usp=sharing
    dict(id="2", german=dict(name="2", description="2 Felder vorwärts")),
    dict(id="3", german=dict(name="3", description="3 Felder vorwärts")),
    dict(id="4", german=dict(name="4", description="4 Felder vorwärts oder rückwärts")),
    dict(id="5", german=dict(name="5", description="5 Felder vorwärts")),
    dict(id="6", german=dict(name="6", description="6 Felder vorwärts")),
    dict(id="7", german=dict(name="7", description="7 Eingelschritte vorwärts. Einzelschritte können auf verschiedene Kugeln aufgeteilt werden.")),
    dict(id="8", german=dict(name="8", description="8 Felder vorwärts")),
    dict(id="9", german=dict(name="9", description="9 Felder vorwärts")),
    dict(id="10", german=dict(name="10", description="10 Felder vorwärts")),
    dict(id="ace", german=dict(name="Ass", description="Eine Kugel zum Start bewegen oder 11 Felder vorwärts oder 1 Feld vorwärts")),
    dict(id="jack", german=dict(name="Junge", description="Eigene Kugel mit einer fremden Kugel tauschen")),
    dict(id="queen", german=dict(name="Dame", description="12 Felder vorwärts")),
    dict(id="king", german=dict(name="König", description="Eige Kugel zum Start bewegen oder 13 Felder vorwärts")),
)

JOKER = dict(id="joker", german=dict(name="Joker", description="Karte nach Wunsch. Als letzte Karte zum Sieg darf der Joker nicht gelegt werden."))

class Card:
    def __init__(self, dict_card: dict, color: str):
        assert color in ('',) + COLOURS
        self.__dict_card = dict_card
        self.__color = color

    @property
    def id(self) -> str:
        return self.__dict_card['id']

    @property
    def filebase(self) -> str:
        return f'{self.id}{self.__color}'

    @property
    def nameI18N(self) -> str:
        return self.__dict_card['german']['name']

    @property
    def descriptionI18N(self) -> str:
        return self.__dict_card['german']['description']

class Cards:
    @classmethod
    def create_cards(cls):
        for _set in range(2): # Two sets
            for color in COLOURS: # Four colours
                for dict_card in LIST_4_COLOURS:
                    yield Card(dict_card, color)
            for _jokers in range(3): # 3 Jokers
                yield Card(JOKER, '')

    @classmethod
    def all_cards(cls):
        return list(Cards.create_cards())

    def __init__(self):
        self.__list_cards = Cards.all_cards()

    @property
    def all(self) -> list:
        return self.__list_cards

    @property
    def count(self):
        return len(self.__list_cards)

    def shuffle(self, f):
        f(self.__list_cards)

    def pop_card(self) -> Card:
        return self.__list_cards.pop()

    def pop_cards(self, count:int) -> list:
        list_cards = self.__list_cards[:count]
        self.__list_cards = self.__list_cards[count:]
        return sorted(list_cards, key=lambda card: card.id)

# ALL_CARDS = [Card(dict_card) for dict_card in Cards.create_cards()]

if __name__ == '__main__':
    pass
