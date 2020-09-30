#! /bin/python3
import argparse
import chord_format
import format_chordpro as chordpro
import format_space as space
import os
import re
import song
import sys

formats = [
    chordpro.format,
    space.format,
]

try:
    import format_ug as ug
    formats.append(ug.format)
except:
    pass

# validate formats
for f in formats:
    assert chord_format.valid_format(f), 'Bricked format: {}'.format(f)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def save(exported_song, path, args):
    if args.output_path:
        if os.path.isfile(path) and not args.force:
            eprint('WARNING: File {} already exists and will NOT be overwritten!'.format(path))
            return False, path
        elif os.path.isdir(path):
            # create filename of format 'filename.end' or 'filename3.end'
            filename = '{}.{}'.format(exported_song.get_filename(), exported_song.format['file_endings'][0])
            path = os.path.join(path, filename)
            if os.path.exists(path) and not args.force:
                eprint('WARNING: File {} already exists and will NOT be overwritten!'.format(path))
                return False, path
            with open(path, 'w') as file:
                file.write(exported_song.content)
            return True, path
        elif not os.path.isfile(path) or args.force:
            with open(path, 'w') as file:
                file.write(exported_song.content)
            return True, path
        else:
            return False, path


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
    if 'format_ug' in sys.modules and re.match(r'https://tabs.ultimate-guitar.com/.*[0-9]{4,10}', url):
        return ug.format['importeur']
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
    return parser.parse_args()


def main():
    args = parse_args()

    if not ',' in args.source and args.source.endswith('.list') and os.path.isfile(args.source):
        with open(args.source, 'r') as f:
            urls = f.readlines()
        for i, url in enumerate(urls):
            urls[i] = url.replace('\n', '')
    else:
        urls = args.source.split(',')

    url_count = len(urls)

    for index, url in enumerate(urls):
        importeur = select_importeur(url)
        export_format = select_format(args.filetype)
        eprint(f'({index + 1}/{url_count}) => {url}')
        eprint(f'\t Importing from {url}')
        imported_song = importeur.load(url)

        eprint(f'\t Exporting to {export_format["identifier"]}')
        exported_song = song.ExportedSong.create(imported_song, export_format)

        if args.output_path:
            success, path = save(exported_song, args.output_path[0], args)
            if success:
                eprint(f'\t Saved to {path}')
            else:
                eprint(f'\t Unable to save song to {path}')
        else:
            print(exported_song.content)

    if 'format_ug' in sys.modules:
        ug.format['importeur'].driver.close()


if __name__ == '__main__':
    main()
