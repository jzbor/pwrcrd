#! /bin/python3
import argparse
import chord_format
import format_chordpro as chordpro
import format_space as space
import os
import re
import song

formats = [
    chordpro.format,
    space.format,
]

# validate formats
for f in formats:
    assert chord_format.valid_format(f), 'Bricked format: {}'.format(f)


def save(exported_song, path, args):
    if args.output_path:
        if os.path.isfile(path) and not args.force:
            print('WARNING: File {} already exists and will NOT be overwritten!').format(path)
            return False
        elif os.path.isdir(path):
            # create filename of format 'filename.end' or 'filename3.end'
            filename = '{}{{}}.{}'.format(exported_song.get_filename(), exported_song.format['file_endings'][0])
            if os.path.exists(os.path.join(path, filename.format(''))) and not args.force:
                i = 1
                while os.path.exists(os.path.join(path, filename.format(i))):
                    i += 1
                filename = filename.format(i)
            else:
                filename = filename.format('')
            path = os.path.join(path, filename)
            file = open(path, 'w')
            file.write(exported_song.content)
            file.close()
            return True
        elif not os.path.isfile(path) or args.force:
            file = open(path, 'w')
            file.write(exported_song.content)
            file.close()
            return True
        else:
            return False


def select_exporteur(identifier):
    for f in formats:
        if f['identifier'] == identifier:
            return f['exporteur']
    print('Output format {} not available'.format(identifier))
    exit(1)


def select_format(identifier):
    for f in formats:
        if f['identifier'] == identifier:
            return f
    print('Output format {} not available'.format(identifier))
    exit(1)


def select_importeur(url):
    # Returns the importeur of the according class
    for f in formats:
        if re.sub(r'.*\.', '', url) in f['file_endings']:
            return f['importeur']
    print('No format found for "{}"'.format(url))
    exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Convert chords between multiple formats')
    parser.add_argument('source', help='source file(s) or list', type=str)
    parser.add_argument('filetype', help='output filetype', type=str)
    parser.add_argument('-o', '--output-file', help='output file or directory',
                        nargs=1, dest='output_path')
    parser.add_argument('-f', '--force', help='overwrite existing files',
                        action='store_true')
    # @TODO Following functions to be implemented
    # * delete source files
    # * verbosity
    # * generate pdf (via latex or chord pro)
    return parser.parse_args()


def main():
    args = parse_args()

    urls = args.source.split(',')

    for url in urls:
        importeur = select_importeur(url)
        export_format = select_format(args.filetype)
        imported_song = importeur.load(url)

        print(imported_song)
        print(imported_song.meta)

        exported_song = song.ExportedSong.create(imported_song, export_format)

        if args.output_path:
            save(exported_song, args.output_path[0], args)
        else:
            print(exported_song.content)


if __name__ == '__main__':
    main()
