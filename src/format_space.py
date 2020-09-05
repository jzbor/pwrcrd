import chord_format
import os
import os.path
import re
import song

from song import MetaType

#shortcuts for chord and lyric lines
cl = lambda a : a * 2
ll = lambda a : a * 2 + 1


class Importeur(chord_format.Importeur):
    """Importeur to parse the external format into the internal data structure."""
    def __init__(self):
        pass

    def parse_metadata(self, lines, imported_song):
        """Filters out title, artist and metadata and returns all regular lines"""
        # global metadata
        imported_song.title = lines[0]
        imported_song.artist = lines[1]
        lines = lines[2:]
        removed_lines = 0
        for line in lines.copy():
            match = re.match(r'\$[a-z]* (.*)', line)
            if match:
                if match.group(1) == 'capo':
                    song.capo = match.group(2)
                lines.remove(line)
                removed_lines+=1
            else:
                break
        # Even out lines after header (for chord matching)
        if removed_lines % 2 != 0:
            lines.pop(0)

        # @TODO implement comments

        # find choruses
        chorus_pattern = r'    .*'
        chorus_start = 0
        chorus_end = None
        for i in range(len(lines) // 2):
            if re.match(chorus_pattern, lines[ll(i)]) \
                    or re.match(chorus_pattern, lines[cl(i)]) and lines[ll(i)] == '':
                chorus_end = i + 1
                lines[cl(i)] = lines[cl(i)][4:]
                lines[ll(i)] = lines[ll(i)][4:]
            else:
                if chorus_start and chorus_end and chorus_start <= chorus_end:
                    imported_song.meta.append((chorus_start, chorus_end, MetaType.CHORUS, None))
                chorus_start = i + 1
        # match chorus if at the end of a song
        if chorus_start and chorus_end and chorus_start <= chorus_end:
            imported_song.meta.append((chorus_start, chorus_end, MetaType.CHORUS, None))
        return lines

    def load(self, url):
        """Return an encoded song."""
        # @TODO Add song title and author
        if not os.path.isfile(url):
            print('{} is no valid chord file'.format(url))
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
                        imported_song.add_chord(li // 2, index, chord)
                        index += len(chord)
            # lyric line
            else:
                imported_song.add_lyrics(line)

        return imported_song


class Exporteur(chord_format.Exporteur):
    """Exporteur to export internal data structure to format"""
    def __init__(self):
        pass

    def insert_metadata(self, lines, song):
        """Inserts the metadata back into the string"""
        simple_tags = {
            MetaType.COMMENT: '\n# {}',
        }
        insert_table = [] # (line_number, string)

        # global metadata
        insert_table.append((0.1, song.title))
        insert_table.append((0.2, song.artist))
        if song.capo:
            insert_table.append((0.3, '$capo {}\n'.format(song.capo)))

        # insert local metadata
        for meta in song.meta:
            if meta[2] == MetaType.CHORUS:
                for i in range(meta[0], meta[1]):
                    lines[cl(i)] = '    {}'.format(lines[cl(i)])
                    lines[ll(i)] = '    {}'.format(lines[ll(i)])
            elif meta[2] in simple_tags.keys():
                insert_table.append((meta[0], simple_tags[meta[2]].format(meta[3])))
            else:
                # Ah this should not happen
                pass
        insert_table = sorted(insert_table)
        next_meta = insert_table.pop(0)
        parsed_string = ''
        for i in range(len(lines) // 2):
            while next_meta and next_meta[1] and int(next_meta[0]) <= int(i):
                parsed_string += next_meta[1] +'\n'
                if insert_table:
                    next_meta = insert_table.pop(0)
                else:
                    # prevent last item in list form being inserted over and over again
                    next_meta = (len(lines) // 2 + 1, None)
                    break
            parsed_string += '{}\n{}\n'.format(lines[cl(i)], lines[ll(i)])
        return parsed_string

    def export(self, song: song.ImportedSong):
        """Return decoded string"""
        assert len(song.chords) > 0

        decoded_string = ''
        chords = song.chords.copy()

        next_chord_line, next_chord_column, next_chord = chords.pop(0)
        for i in range(len(song.lyrics)):
            chord_line = ''
            while next_chord_line <= i and len(chords) > 0:
                if next_chord_line < i:
                    raise Exception('Line of next chord is before current line! (chord: {}; curr: {})'.format(next_chord_line, i))
                for _ in range(next_chord_column - len(chord_line)):
                    chord_line += ' '
                chord_line += next_chord + ' '
                if len(chords) > 0:
                    next_chord_line, next_chord_column, next_chord = chords.pop(0)
                else:
                    break
            decoded_string += chord_line + '\n'
            decoded_string += song.lyrics[i] + '\n'

        return self.insert_metadata(decoded_string.split('\n'), song)


format = {
    'file_endings': ['txt'],
    'identifier': 'space',
    'importeur': Importeur(),
    'exporteur': Exporteur(),
}
