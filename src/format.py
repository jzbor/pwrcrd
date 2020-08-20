import song

class Format:
    # All possible file endings (without dot)
    file_endings = []
    # Identifier: must be unique
    identifier = 'abstracter'

    def __init__(self):
        self.encoder = Encoder()
        self.decoder = Decoder()

    @staticmethod
    def get_encoder():
        return self.encoder

    @staticmethod
    def get_decoder():
        return self.decoder



class Encoder:
    """Encoder to parse the external format into the internal data structure."""
    def __init__(self):
        pass

    def encode(self, url):
        """Return an encoded song."""
        pass

    def encode_chord(self, string):
        """Convert chord if necessary. Return the adjusted chord."""
        return string


class Decoder:
    """Decoder to export internal data structure to format"""
    def __init__(self):
        pass

    def decode(self, song: song.EncodedSong):
        """Return decoded string"""
        pass

    def encode_chord(self, string):
        """Convert chord if necessary. Return the adjusted chord."""
        return string
