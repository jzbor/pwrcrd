import format
import os
import os.path
import re
import song

class Format(format.Format):
    file_endings = ['cho', 'crd', 'chopro', 'chord', 'pro']
    identifier = 'prochord'

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
            print('{} is no valid ProChord file'.format(url))
            return False
        file = open(url)
        lines = file.readlines()

        encoded_song = song.EncodedSong('Unknown', 'Unknown', url)

        # loop over all lines in file
        for li in range(len(lines)):
            line = lines[li]

            # look for artist and title
            match = re.match(r'\{ ?title *: *(.*)}', line)
            if match:
                encoded_song.title = match.group(1)
            else:
                match = re.match(r'\{ ?artist *: *(.*)}', line)
                if match:
                    encoded_song.artist = match.group(1)

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


class Decoder(format.Decoder):
    """Decoder to export internal data structure to format"""
    def __init__(self):
        pass

    def decode(self, song: song.EncodedSong):
        """Return decoded string"""
        decoded_string = ''
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
        return decoded_string

if __name__ == '__main__':
    # @TODO Only for test purposes - remove afterwards
    encoder = Encoder()
    decoder = Decoder()
    song = encoder.encode('/home/jzbor/Programming/Python/PwrCrd/test/example.cho')
    if song:
        print(song.chords, song.lyrics)
        print()
        print(decoder.decode(song))

