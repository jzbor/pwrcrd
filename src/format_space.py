import format
import os
import os.path
import re
import song
import format_prochord

class Format(format.Format):
    file_endings = ['txt']
    identifier = 'space'

    def __init__(self):
        self.encoder = Encoder()
        self.decoder = Decoder()

class Encoder(format.Encoder):
    """Encoder to parse the external format into the internal data structure."""
    def __init__(self):
        pass

    def encode(self, url):
        """Return an encoded song."""
        # @TODO Add song title and author
        if not os.path.isfile(url):
            print('{} is no valid chord file'.format(url))
            return False
        file = open(url)
        lines = file.readlines()

        if len(lines) < 2:
            print('{} is no valid chord file'.format(url))
            return False

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')

        encoded_song = song.EncodedSong(lines[0], lines[1], url)
        lines = lines[2:]

        # loop over all lines in file
        for li in range(len(lines)):
            line = lines[li]

            # chord line
            if li % 2 == 0:
                index = 0
                while len(line) > 0:
                    if line[0] == ' ':
                        line = line[1:]
                        index += 1
                    else:
                        if ' ' in line:
                            chord = line[:line.find(' ')]
                            line = line[line.find(' '):]
                        else:
                            chord = line
                            line = ''
                        encoded_song.add_chord(li // 2, index, chord)
                        index += len(chord)
            # lyric line
            else:
                encoded_song.add_lyrics(line)


        return encoded_song


class Decoder(format.Decoder):
    """Decoder to export internal data structure to format"""
    def __init__(self):
        pass

    def decode(self, song: song.EncodedSong):
        """Return decoded string"""
        assert len(song.chords) > 0

        decoded_string = ''
        chords = song.chords.copy()

        # header
        decoded_string += song.title + '\n'
        decoded_string += song.artist + '\n'
        if not song.lyrics[0] == '':
            decoded_string += '\n\n'

        next_chord_line, next_chord_column, next_chord = chords.pop(0)
        for i in range(len(song.lyrics)):
            chord_line = ''
            while next_chord_line <= i and len(chords) > 0:
                if next_chord_line < i:
                    raise Exception('Line of next chord is before current line! (chord: {}; curr: {})'.format(next_chord_line, i))
                for _ in range(next_chord_column - len(chord_line)):
                    chord_line += ' '
                chord_line += next_chord
                if len(chords) > 0:
                    next_chord_line, next_chord_column, next_chord = chords.pop(0)
                else:
                    break
            decoded_string += chord_line + '\n'
            decoded_string += song.lyrics[i] + '\n'

        return decoded_string
