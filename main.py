import json
from dataclasses import asdict

import network
import parsers


def main():
    # replaces_page = network.fetch_replaces_page()
    with open('tmp.txt', mode='rb') as file:
        replaces = parsers.parse_replaces(file.read())

    print(replaces)


if __name__ == '__main__':
    main()
