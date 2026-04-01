from __future__ import annotations

import dataclasses
import enum
from collections.abc import Callable


class Colour(enum.StrEnum):
    C = "C"
    D = "D"
    H = "H"
    S = "S"
    NONE = ""


@dataclasses.dataclass(frozen=True)
class Language:
    name: str
    description: str


@dataclasses.dataclass(frozen=True  )
class CardDef:
    id: str
    languages: dict[str, Language]


LIST_4_COLOURS = (
    # https://docs.google.com/spreadsheets/d/1fnAL9Csg0xfkZqHPyxq1r5kL7MLX200DlCBzDXKeito/edit?usp=sharing
    CardDef(id="2", languages={"german": Language(name="2", description="2 Felder vorwärts")}),
    CardDef(id="3", languages={"german": Language(name="3", description="3 Felder vorwärts")}),
    CardDef(id="4", languages={"german": Language(name="4", description="4 Felder vorwärts oder rückwärts")}),
    CardDef(id="5", languages={"german": Language(name="5", description="5 Felder vorwärts")}),
    CardDef(id="6", languages={"german": Language(name="6", description="6 Felder vorwärts")}),
    CardDef(
        id="7",
        languages={
            "german": Language(
                name="7",
                description="7 Eingelschritte vorwärts. Einzelschritte können auf verschiedene Kugeln aufgeteilt werden.",
            )
        },
    ),
    CardDef(id="8", languages={"german": Language(name="8", description="8 Felder vorwärts")}),
    CardDef(id="9", languages={"german": Language(name="9", description="9 Felder vorwärts")}),
    CardDef(id="10", languages={"german": Language(name="10", description="10 Felder vorwärts")}),
    CardDef(
        id="ace",
        languages={
            "german": Language(
                name="Ass",
                description="Eine Kugel zum Start bewegen oder 11 Felder vorwärts oder 1 Feld vorwärts",
            )
        },
    ),
    CardDef(
        id="jack",
        languages={"german": Language(name="Junge", description="Eigene Kugel mit einer fremden Kugel tauschen")},
    ),
    CardDef(id="queen", languages={"german": Language(name="Dame", description="12 Felder vorwärts")}),
    CardDef(
        id="king",
        languages={
            "german": Language(
                name="König",
                description="Eige Kugel zum Start bewegen oder 13 Felder vorwärts",
            )
        },
    ),
)

JOKER = CardDef(
    id="joker",
    languages={
        "german": Language(
            name="Joker",
            description="Karte nach Wunsch. Als letzte Karte zum Sieg darf der Joker nicht gelegt werden.",
        )
    },
)

@dataclasses.dataclass(frozen=True)
class CardDefColor:
    card_def: CardDef
    color: Colour

    @property
    def id(self) -> str:
        return self.card_def.id

    @property
    def filebase(self) -> str:
        return f"{self.id}{self.color}"

    @property
    def name_i18n(self) -> str:
        return self.card_def.languages["german"].name

    @property
    def description_i18n(self) -> str:
        return self.card_def.languages["german"].description


class Cards(list[CardDefColor]):
    def __init__(self) -> None:
        super().__init__(
            CardDefColor(card_def, color)
            for _set in range(2)
            for color in (Colour.C, Colour.D, Colour.H, Colour.S)
            for card_def in LIST_4_COLOURS
        )
        for _jokers in range(3):  # 3 Jokers
            self.append(CardDefColor(JOKER, Colour.NONE))

    @property
    def all(self) -> Cards:
        return self

    @property
    def card_count(self) -> int:
        return len(self)

    def shuffle(self, f: Callable[[Cards], None]) -> None:
        f(self)

    def pop_card(self) -> CardDefColor:
        return self.pop()

    def pop_cards(self, count: int) -> Cards:
        result = Cards.__new__(Cards)
        list.__init__(result, sorted(self[:count], key=lambda card: card.id))
        del self[:count]
        return result


if __name__ == "__main__":
    pass
