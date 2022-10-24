from urllib.parse import urlparse
from typing import Optional

import bs4
from loguru import logger

import model


def parse_replaces_base(page: str) -> str:
    # r = session.get(url=MAIN_SITE_URL, params=MAIN_SITE_PARAMS)
    # r.raise_for_status()

    souped = bs4.BeautifulSoup(page, 'html.parser')
    a = souped.find('a', text="Замены в расписании", attrs={'class': 'sublevel'})
    link = a['href']

    parsed = urlparse(link)
    netloc = parsed.netloc
    scheme = parsed.scheme

    return scheme + '://' + netloc


def parse_replaces(page: bytes) -> model.Replaces:
    # r = session.get(endpoint)
    # r.raise_for_status()

    souped = bs4.BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
    the_table = souped.find('table')

    header: Optional[str] = None
    groups: dict[int, model.GroupReplaces] = dict()

    expecting_group_header = False
    current_group: Optional[int] = None

    for tr in the_table:
        td: bs4.element.Tag = tr.contents[0]
        td_class: str = td['class'][0]

        if td_class == 'header':
            logger.debug(f'header: {td}')
            if header is not None:
                logger.warning('Met second header', page)

            header = td.string

        elif td_class == 'footer':
            logger.debug(f'Footer: {td.string}')

        elif td_class == 'section':  # Group number row
            logger.debug(f'section: {td}')
            current_group = int(td.string)
            groups[current_group] = model.GroupReplaces(current_group, dict())
            expecting_group_header = True  # After section goes group header

        elif td_class == 'content':
            if not expecting_group_header:
                logger.debug(f'Group row: {tr}')
                replace = model.replace_from_tr(tr)
                if current_group is None:
                    logger.warning('Current group is None', page)

                groups[current_group].group_replaces.update({replace.lesson_number: replace})

            else:
                expecting_group_header = False
                if td.string != '№ пары':
                    logger.warning('expecting group header and do not got one', page)

    return model.Replaces(header=header, groups=groups)
