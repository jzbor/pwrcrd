import chord_format
import os
import os.path
import re
import song


class Importeur(chord_format.Importeur):
    """Importeur to parse the external format into the internal data structure."""
    def __init__(self):
        pass

    def load(self, url):
        """Return an encoded song."""
        # @TODO Add song title and author
        if not os.path.isfile(url):
            print('{} is no valid ProChord file'.format(url))
            return False
        file = open(url)
        lines = file.readlines()

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')

        title = 'Unknown'
        artist = 'Unknown'
        # Filter comments and metadata
        for line in lines.copy():
            if line.startswith('{'):
                lines.remove(line)

            # look for artist and title
            match = re.match(r'\{ ?title *: *(.*)}', line)
            if match:
                title = match.group(1)
            else:
                match = re.match(r'\{ ?artist *: *(.*)}', line)
                if match:
                    artist = match.group(1)

        encoded_song = song.ImportedSong(title, artist, url)

        # loop over all lines in file
        for li in range(len(lines)):
            line = lines[li]

            # parse chords while there are start and end marks of chords
            while '[' in line and ']' in line:
                index = line.find('[')
                chord = line[line.find('[') + 1: line.find(']')]
                chord = self.encode_chord(chord)
                encoded_song.add_chord(li, index, chord)

                # Remove current chord from line
                line = re.sub(r'\[.*?\]', '', line, count=1)
            encoded_song.add_lyrics(line)
        return encoded_song


class Exporteur(chord_format.Exporteur):
    """Exporteur to export internal data structure to format"""
    def __init__(self):
        pass

    def export(self, song: song.ImportedSong):
        """Return decoded string"""
        decoded_string = ''

        # insert title and author
        decoded_string += '{{title: {}}}\n'.format(song.title)
        decoded_string += '{{artist: {}}}\n'.format(song.artist)

        chords = song.chords.copy()
        next_chord_line, next_chord_column, next_chord = chords.pop(0)
        for i in range(len(song.lyrics)):
            lyric_line = song.lyrics[i]
            for j in range(len(lyric_line)):
                if next_chord_line > i:
                    # Write rest of the line if there is no chord left in it
                    decoded_string += lyric_line[j:]
                    break
                elif next_chord_line == i or not chords:
                    # Append chord if necessary
                    if next_chord_column == j:
                        decoded_string += '['+next_chord+']'
                        if chords:
                            next_chord_line, next_chord_column, next_chord = chords.pop(0)
                    # Append next char from lyrics
                    decoded_string += lyric_line[j]
                else:
                    raise Exception('Line of next chord is before current line! (chord: {}; curr: {})'.format(next_chord_line, i))
            decoded_string += '\n'
        return decoded_string


format = {
    'file_endings': ['cho', 'crd', 'chopro', 'chord', 'pro'],
    'identifier': 'prochord',
    'importeur': Importeur(),
    'exporteur': Exporteur(),
}
