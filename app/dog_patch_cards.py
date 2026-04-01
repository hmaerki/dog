from __future__ import annotations

import pathlib
import xml.sax
import xml.sax.saxutils
import xml.sax.xmlreader

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()
DIRECTORY_CARDS_ORI = DIRECTORY_OF_THIS_FILE / "static" / "img" / "cardsori"
DIRECTORY_CARDS_NEW = DIRECTORY_OF_THIS_FILE / "static" / "img" / "cards"


class CardsPatcher(xml.sax.saxutils.XMLFilterBase):
    def __init__(self) -> None:
        parent = xml.sax.make_parser()
        super().__init__(parent)
        self.__rect: dict[str, str] | None = None

    def startElement(self, name: str, attrs: xml.sax.xmlreader.AttributesImpl) -> None:  # type: ignore[override]
        if name == "svg":
            # width="2.25in" height="3.5in"
            card_width = 45
            card_height = 70
            attrs_dict: dict[str, str] = {key: value for key, value in attrs.items()}
            attrs_dict["height"] = f"{card_height}"
            attrs_dict["width"] = f"{card_width}"
            attrs_dict["x"] = f"{-card_width / 2}"
            attrs_dict["y"] = f"{-card_height / 2}"
            super().startElement(name, attrs_dict)  # type: ignore[arg-type]
            return

        if name == "rect":
            self.__rect = {key: value for key, value in attrs.items()}
            self.__rect["stroke"] = "blue"
            self.__rect["stroke-width"] = "0"
            super().startElement(name, self.__rect)  # type: ignore[arg-type]
            return

        super().startElement(name, attrs)

    def convert_cards(self) -> None:
        if not DIRECTORY_CARDS_NEW.exists():
            DIRECTORY_CARDS_NEW.mkdir(parents=True)

        for filename_ori in DIRECTORY_CARDS_ORI.glob("*.svg"):
            filename_new = DIRECTORY_CARDS_NEW.joinpath(filename_ori.name)
            # print(f'*** {filename_ori} -> {filename_new}')

            reader = CardsPatcher()
            with filename_new.open("w", encoding="utf-8") as f:
                handler = xml.sax.saxutils.XMLGenerator(f, encoding="utf-8")
                reader.setContentHandler(handler)
                reader.parse(str(filename_ori))


if __name__ == "__main__":
    cp = CardsPatcher()
    cp.convert_cards()
