#! /bin/python3
import argparse
import re

import chord_format
import format_prochord as prochord
import format_space as space

formats = [
    prochord.format,
    space.format,
]

# validate formats
for f in formats:
    assert chord_format.valid_format(f), 'Bricked format: {}'.format(f)


def select_importeur(url):
    # Returns the importeur of the according class
    for f in formats:
        if re.sub(r'.*\.', '', url) in f['file_endings']:
            return f['importeur']
    print('No format found for "{}"'.format(url))
    exit(1)


def select_exporteur(identifier):
    for f in formats:
        if f['identifier'] == identifier:
            return f['exporteur']
    print('Output format {} not available'.format(identifier))
    exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Convert chords between multiple formats')
    parser.add_argument('source', help='source file(s) or list', type=str)
    parser.add_argument('filetype', help='output filetype', type=str)
    # Following args should be defined:
    # * output formats to generate/keep
    # * input file/url/format
    # * overwrite existing files
    # * verbosity
    return parser.parse_args()


def main():
    args = parse_args()

    urls = args.source.split(',')

    for url in urls:
        importeur = select_importeur(url)
        exporteur = select_exporteur(args.filetype)
        song = importeur.load(url)
        print(exporteur.export(song))


if __name__ == '__main__':
    main()
