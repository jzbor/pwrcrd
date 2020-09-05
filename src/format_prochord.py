import chord_format
import os
import os.path
import re
import song

from song import MetaType


class Importeur(chord_format.Importeur):
    """Importeur to parse the external format into the internal data structure."""
    def __init__(self):
        pass

    def parse_metadata(self, lines, imported_song):
        """Filters out title, artist and metadata and returns all regular lines"""
        chorus_start = 0
        li = 0
        for line in lines.copy():
            tags = {
                r'\{ ?title *: *(.*)}': 'title',
                r'\{ ?artist *: *(.*)}': 'artist',
                r'\{ ?capo *: *(.*)}': MetaType.CAPO,
                r'\{ ?comment *: *(.*)}': MetaType.COMMENT,
                r' *\# *(.*)': MetaType.HIDDEN_COMMENT,
                r'\{ ?(start_of_chorus) ?}': MetaType.CHORUS,
                r'\{ ?(end_of_chorus) ?}': MetaType.CHORUS,
            }

            matched = False
            for regex in tags.keys():
                match = re.match(regex, line)
                if match:
                    if tags[regex] == 'title':
                        imported_song.title = match.group(1)
                    elif tags[regex] == 'artist':
                        imported_song.artist = match.group(1)
                    elif tags[regex] == MetaType.CAPO:
                        imported_song.capo = match.group(1)
                    elif tags[regex] == MetaType.COMMENT:
                        imported_song.add_metadata(li, li, MetaType.COMMENT, match.group(1))
                    elif tags[regex] == MetaType.HIDDEN_COMMENT:
                        imported_song.add_metadata(li, li, MetaType.HIDDEN_COMMENT, match.group(1))
                    elif tags[regex] == MetaType.CHORUS:
                        if match.group(1) == 'start_of_chorus':
                            chorus_start = li
                        else:
                            imported_song.add_metadata(chorus_start, li, MetaType.CHORUS)
                    else:
                        # @TODO better handling of this exception
                        print('THERE IS AN ERROR IN THE CODE!!!')
                        matched = False
                        break
                    matched = True
                    break
            if matched:
                lines.remove(line)
            else:
                li += 1

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

        encoded_song = song.ImportedSong('Unknown', 'Unknown', url)
        self.parse_metadata(lines, encoded_song)

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

    def insert_metadata(self, lines, song):
        """Inserts the metadata back into the string"""
        simple_tags = {
            MetaType.COMMENT: '{ comment: {} }',
            MetaType.HIDDEN_COMMENT: '# {}',
        }
        insert_table = [] # (line_number, string)

        # global metadata
        insert_table.append((0, '{{ title: {} }}'.format(song.title)))
        insert_table.append((0, '{{ artist: {} }}'.format(song.artist)))
        if song.capo:
            insert_table.append((0, '{{ capo: {} }}'.format(song.capo)))

        # insert local metadata
        # comment, hidden comment, soc, eoc
        # format of metadata: (line_start: int, line_end: int, type: MetaType, value: str)
        for meta in song.meta:
            # @ TODO check possible bug: comment moving out of/into chorus
            if meta[2] == MetaType.CHORUS:
                insert_table.append((meta[0], '{ start_of_chorus }'))
                insert_table.append((meta[1], '{ end_of_chorus }'))
            elif meta[2] in simple_tags.keys():
                insert_table.append((meta[0], simple_tags[meta[2]].format(meta[3])))
            else:
                # Ah this should not happen
                pass
        insert_table = sorted(insert_table)
        next_meta = insert_table.pop(0)
        parsed_string = ''
        i = 0
        for line in lines:
            while next_meta[0] <= i:
                parsed_string += next_meta[1] + '\n'
                if insert_table:
                    next_meta = insert_table.pop(0)
                else:
                    break
            parsed_string += line + '\n'
            i += 1
        return parsed_string

    def export(self, song: song.ImportedSong):
        """Return decoded string"""
        decoded_string = ''

        chords = song.chords.copy()
        next_chord_line, next_chord_column, next_chord = chords.pop(0)
        for i in range(len(song.lyrics)):
            lyric_line = song.lyrics[i]
            length = max(1, len(lyric_line))
            for j in range(length):
                if next_chord_line > i:
                    # Write rest of the line if there is no chord left in it
                    decoded_string += lyric_line[j:]
                    break
                elif next_chord_line == i or not chords:
                    # Append chord if necessary
                    while chords and next_chord_line == i and next_chord_column == j:
                        decoded_string += '['+next_chord+']'
                        if chords:
                            next_chord_line, next_chord_column, next_chord = chords.pop(0)
                    # Append next char from lyrics
                    if j < len(lyric_line):
                        decoded_string += lyric_line[j]
                else:
                    raise Exception('Line of next chord is before current line! (chord: {}; curr: {})'.format(next_chord_line, i))
            decoded_string += '\n'

        return self.insert_metadata(decoded_string.split('\n'), song)


format = {
    'file_endings': ['cho', 'crd', 'chopro', 'chord', 'pro'],
    'identifier': 'prochord',
    'importeur': Importeur(),
    'exporteur': Exporteur(),
}
