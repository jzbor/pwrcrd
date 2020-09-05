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

        # @TODO Fix bug: trailing spaces on title and artist
        tags = {
            r'\{ ?title *: *(.*)}': 'title',
            r'\{ ?artist *: *(.*)}': 'artist',
            r'\{ ?capo *: *(.*)}': MetaType.CAPO,
            r'\{ ?comment *: *(.*)}': MetaType.COMMENT,
            r' *\# *(.*)': MetaType.HIDDEN_COMMENT,
            r'\{ ?(start_of_chorus) ?}': MetaType.CHORUS,
            r'\{ ?(end_of_chorus) ?}': MetaType.CHORUS,
        }
        for line in lines.copy():
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
        return lines

    def load(self, url):
        """Return an encoded song."""
        # @TODO Add song title and author
        if not os.path.isfile(url):
            print('{} is no valid chordpro file'.format(url))
            return False
        file = open(url)
        lines = file.readlines()

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')

        imported_song = song.ImportedSong('Unknown', 'Unknown', url)
        lines = self.parse_metadata(lines, imported_song)

        # loop over all lines in file
        for li in range(len(lines)):
            line = lines[li]

            # parse chords while there are start and end marks of chords
            while '[' in line and ']' in line:
                index = line.find('[')
                chord = line[line.find('[') + 1: line.find(']')]
                chord = self.encode_chord(chord)
                imported_song.add_chord(li, index, chord)

                # Remove current chord from line
                line = re.sub(r'\[.*?\]', '', line, count=1)
            imported_song.add_lyrics(line)
        return imported_song


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
        insert_table.append((0.1, '{{ title: {} }}'.format(song.title)))
        insert_table.append((0.2, '{{ artist: {} }}'.format(song.artist)))
        if song.capo:
            insert_table.append((0.3, '{{ capo: {} }}'.format(song.capo)))

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
        for i in range(len(lines)):
            while next_meta and next_meta[1] and int(next_meta[0]) <= i:
                parsed_string += next_meta[1] + '\n'
                if insert_table:
                    next_meta = insert_table.pop(0)
                else:
                    # prevent last item in list form being inserted over and over again
                    next_meta = (len(lines) // 2 + 1, None)
                    break
            parsed_string += '{}\n'.format(lines[i])
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
                    while chords and next_chord_line == i \
                            and (next_chord_column == j or next_chord_column >= len(lyric_line)):
                        decoded_string += '['+next_chord+']'
                        if chords:
                            next_chord_line, next_chord_column, next_chord = chords.pop(0)
                    # Append next char from lyrics
                    if j < len(lyric_line):
                        decoded_string += lyric_line[j]
                else:
                    print(decoded_string)
                    print(next_chord_line, next_chord_column, next_chord)
                    print(chords)
                    raise Exception('Line of next chord is before current line! (chord: {}; curr: {})'.format(next_chord_line, i))
            decoded_string += '\n'

        return self.insert_metadata(decoded_string.split('\n'), song)


format = {
    'file_endings': ['cho', 'crd', 'chopro', 'chord', 'pro'],
    'identifier': 'chordpro',
    'importeur': Importeur(),
    'exporteur': Exporteur(),
}
