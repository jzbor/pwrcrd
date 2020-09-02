import song


def valid_format(f):
    if type(f) != dict:
        return False
    for key in format.keys():
        if key not in f.keys():
            return False
        if not isinstance(f[key], type(format[key])):
            return False
    return True


class Importeur:
    """Importeur to parse the external format into the internal data structure."""

    def __init__(self):
        pass

    def load(self, url):
        """Return an encoded song."""
        pass

    def encode_chord(self, string):
        """Convert chord if necessary. Return the adjusted chord."""
        return string


class Exporteur:
    """Exporteur to export internal data structure to format"""

    def __init__(self):
        pass

    def export(self, song: song.ImportedSong):
        """Return decoded string"""
        pass

    def encode_chord(self, string):
        """Convert chord if necessary. Return the adjusted chord."""
        return string


format = {
    'file_endings': [],
    'identifier': 'abstract',
    'importeur': Importeur(),
    'exporteur': Exporteur(),
}
