import json
import chardet
from PIL import Image
from PIL import ImageDraw
from src.constant import COLORS

DEFAULT_BYTE_SIZE = 10
DEFAULT_MARGIN_SIZE = 50


class SeeSoft:
    def __init__(self, path: str, comments=True):
        with open(path) as f:
            self.data = json.load(f)

        self.comments = comments
        self.source_code = self.__read_source_code()
        self.bytes = [dict() for _ in range(len(self.source_code))]

    def __read_source_code(self) -> str:
        raw_data = open(self.data['path'], 'rb').read()
        chardet_result = chardet.detect(raw_data)

        if chardet_result['encoding'] not in ['ascii', 'utf-8']:
            raw_data = raw_data.decode('iso-8859-1').encode('utf-8')

        return raw_data.decode("utf-8")

    def __add_color(self, node: dict):
        position = node['position'] - 1
        for i in range(position, position + node['characters_count']):
            self.bytes[i]['container'] = node['container']
            self.bytes[i]['char'] = self.source_code[i]

            if 'children' in node:
                for child in node['children']:
                    self.__add_color(child)

    def __build_byte_table(self):
        # assign container to each character form source code
        for node in self.data['nodes']:
            self.__add_color(node)

        # add None container to characters which don't belong anywhere
        for i, byte in enumerate(self.bytes):
            if not byte:
                byte['container'] = None
                byte['char'] = self.source_code[i]

            if byte['char'] == '\n':
                byte['container'] = None

        # remove '\r'
        self.bytes = list(filter(lambda b: b['char'] != '\r', self.bytes))

        if self.comments:
            # add comments and other code segments which don't belong to any
            # container to 'comment' container
            for byte in self.bytes:
                if not byte['container'] and not byte['char'].isspace():
                    byte['container'] = 'comment'

            # make spaces in comments colorful instead of white
            for i, byte in enumerate(self.bytes):
                if (
                        byte['char'] == ' '
                        and i - 1 >= 0
                        and i + 1 < len(self.bytes)
                        and self.bytes[i - 1]['container'] == 'comment'
                        and self.bytes[i + 1]['container'] == 'comment'
                ):
                    byte['container'] = 'comment'

        else:
            # delete comments and code segments without container
            self.bytes = list(
                filter(lambda b: b['container'] or b['char'] == '\n',
                       self.bytes)
            )

        # remove empty lines from te beginning of the file
        while self.bytes[0]['char'].isspace():
            del self.bytes[0]

        # handle white spaces in the beginning of the line
        # it's about keeping tabs white in the final image
        for i, byte in enumerate(self.bytes):
            if byte['char'] == '\n':
                j = i + 1

                while (j < len(self.bytes) and
                       self.bytes[j]['char'].isspace()):
                    self.bytes[j]['container'] = None
                    j += 1

        # reduce empty lines sequence to <= 2
        i = 0
        while i < len(self.bytes) - 3:
            if (self.bytes[i]['char'] == '\n'
                    and self.bytes[i + 1]['char'] == '\n'
                    and self.bytes[i + 2]['char'] == '\n'
                    and self.bytes[i + 3]['char'] == '\n'):
                del self.bytes[i]
            else:
                i += 1

    def __max_line(self) -> int:
        max_len = 0
        local_len = 0

        for byte in self.bytes:
            if byte['char'] == '\n':
                if local_len > max_len:
                    max_len = local_len
                local_len = 0
            elif byte['char'] == '\t':
                local_len += 4
            else:
                local_len += 1

        return max_len

    def __lines_count(self) -> int:
        count = 1

        for byte in self.bytes:
            if byte['char'] == '\n':
                count += 1

        return count

    def draw(self, byte_size=None, margin_size=None, filename=None):
        byte_size = byte_size or DEFAULT_BYTE_SIZE
        margin_size = margin_size or DEFAULT_MARGIN_SIZE

        self.__build_byte_table()

        width = (self.__max_line() * byte_size) + 2 * margin_size
        height = (self.__lines_count() * byte_size) + 2 * margin_size
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        row = 0
        column = 0
        for byte in self.bytes:

            if byte['char'] == '\n':
                row += 1
                column = 0
            elif byte['char'] == '\t':
                # when the character is '\t' just write rectangle of size 4
                x = margin_size + column * byte_size
                y = margin_size + row * byte_size
                draw.rectangle(
                    (x, y, x + 4 * byte_size, y + byte_size),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 4
            else:
                x = margin_size + column * byte_size
                y = margin_size + row * byte_size
                draw.rectangle(
                    (x, y, x + byte_size, y + byte_size),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 1

        image.save(filename or 'image.png')
