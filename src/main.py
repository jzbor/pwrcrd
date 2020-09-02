#! /bin/python3
import argparse
import re
import format_prochord as prochord
import format_space as space

formats = {
    prochord.Format.identifier: prochord.Format(),
    space.Format.identifier: space.Format(),
}

def select_encoder(url):
    # Returns the encoder of the according class
    if re.sub('.*\.', '', url) in prochord.Format.file_endings:
        return formats[prochord.Format.identifier].encoder
    elif re.sub('.*\.', '', url) in space.Format.file_endings:
        return formats[space.Format.identifier].encoder
    else:
        print('No format found for "{}"'.format(url))
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
        encoder = select_encoder(url)
        decoder = formats[args.filetype].decoder
        song = encoder.encode(url)
        print(decoder.decode(song))




if __name__ == '__main__':
    main()
