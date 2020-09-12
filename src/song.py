from enum import Enum

class MetaType(Enum):
    # global meta types (whole song)
    TITLE = 1
    ARTIST = 2
    CAPO = 3
    # local meta types (specific lines)
    COMMENT = 4
    CHORUS = 5
    # VERSE = 6 # not supported yet
    # BRIDGE = 7 # not supported yet
    INSERT_CHORUS = 8
    HIDDEN_COMMENT = 9


class Song:
    def __init__(self, title, artist, src_url):
        self.title = title
        self.artist = artist
        self.capo = None
        self.src_url = src_url

    def get_filename(self):
        return '{}-{}'.format(self.artist, self.title).replace(' ', '_')


class SongJob(Song):
    """Job wrapping a song to append to queue"""
    def __init__(self, encoder, decoder, song):
        super().__init__(song.title, song.artist, song.src_url)
        self.encoder = encoder
        self.decoder = decoder

    def run(self):
        pass


class ImportedSong(Song):
    """Song in internal python oop format"""
    def __init__(self, title, artist, src_url):
        super().__init__(title, artist, src_url)
        # format of chords: (line:int, column:int, chord:str)
        self.chords = []
        # format of lyrics: (line:str)
        self.lyrics = []
        # format of metadata: (line_start: int, line_end: int, type: MetaType, value: str)
        # start inclusive; end exclusive
        self.meta = []

    def add_chord(self, line:int, column:int, chord:str):
        self.chords.append((line, column, chord))

    def add_lyrics(self, content:str, line_number:int=-1):
        if line_number == -1:
            self.lyrics.append(content)
        elif line_number < len(self.lyrics):
            self.lyrics[line_number] = content
        else:
            for i in range(len(self.lyrics), line_number):
                self.lyrics.append('')
            self.lyrics.append(content)


    def add_metadata(self, line_start, line_end, metatype, value=''):
        self.meta.append((line_start, line_end, metatype, value))


class ExportedSong(Song):
    def __init__(self, title, artist, src_url, content, export_format):
        super().__init__(title, artist, src_url)
        self.content = content
        self.format = export_format

    @staticmethod
    def create(song:ImportedSong, export_format):
        exporteur = export_format['exporteur']
        return ExportedSong(song.title, song.artist, song.src_url,
                            exporteur.export(song), export_format)
