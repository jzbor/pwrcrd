#! /bin/python3
import argparse
import re
import format_prochord as prochord

formats = {
    prochord.Format.identifier: prochord.Format(),
}

def select_encoder(url):
    # Returns the encoder of the according class
    if re.sub('.*\.', '', url) in prochord.Format.file_endings:
        return formats[prochord.Format.identifier].encoder

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


if __name__ == '__main__':
    main()
