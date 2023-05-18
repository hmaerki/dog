import pathlib
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()
DIRECTORY_CARDS_ORI = DIRECTORY_OF_THIS_FILE / 'static' / 'img' / 'cardsori'
DIRECTORY_CARDS_NEW = DIRECTORY_OF_THIS_FILE / 'static' / 'img' / 'cards'

class CardsPatcher(xml.sax.saxutils.XMLFilterBase):
    def __init__(self):
        parent = xml.sax.make_parser()
        super().__init__(parent)
        self.__rect = None

    def startElement(self, name, attrs):
        if name == 'svg':
            # width="2.25in" height="3.5in"
            card_width = 45
            card_height = 70
            attrs = {key:value for key, value in attrs.items()}
            attrs['height'] = f'{card_height}'
            attrs['width'] = f'{card_width}'
            attrs['x'] = f'{-card_width/2}'
            attrs['y'] = f'{-card_height/2}'

        if name == 'rect':
            self.__rect = {key:value for key, value in attrs.items()}
            self.__rect['stroke'] = 'blue'
            self.__rect['stroke-width'] = '0'
            super().startElement(name, self.__rect)
            return

        super().startElement(name, attrs)

    def convert_cards(self):
        if not DIRECTORY_CARDS_NEW.exists():
            DIRECTORY_CARDS_NEW.mkdir(parents=True)

        for filenameOri in DIRECTORY_CARDS_ORI.glob('*.svg'):
            filenameNew = DIRECTORY_CARDS_NEW.joinpath(filenameOri.name)
            # print(f'*** {filenameOri} -> {filenameNew}')

            reader = CardsPatcher()
            with open(filenameNew, 'w', encoding='utf-8') as f:
                handler = xml.sax.saxutils.XMLGenerator(f, encoding='utf-8')
                reader.setContentHandler(handler)
                reader.parse(str(filenameOri))

if __name__ == '__main__':
    cp = CardsPatcher()
    cp.convert_cards()
