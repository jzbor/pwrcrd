class Song:
    def __init__(self, title, artist, src_url):
        self.title = title
        self.artist = artist
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
        # Format of chords: (line:int, column:int, chord:str)
        self.chords = []
        # Format of lyrics: (line:str)
        self.lyrics = []

    def add_chord(self, line:int, column:int, chord:str):
        self.chords.append((line, column, chord))

    def add_lyrics(self, content:str, line_number:int=-1):
        if line_number == -1:
            self.lyrics.append(content)
        else:
            # May have to initialize list with that size first
            self.lyrics[line_number] = content


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
