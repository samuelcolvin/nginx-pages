#!/usr/bin/env python3

import os
import re
import logging
import shutil
from datetime import datetime
from pathlib import Path
from time import sleep, time
from zipfile import ZipFile

from dateutil.parser import parse
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

logger = logging.getLogger('watch')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)

SLEEP_DURATION = 5
UNPACK_DIR = Path('/var/www/html')
WATCH_DIR = Path('/home/bob/')
FILE_REGEX = r'(\d{4}.*?)\.zip$'


def build():
    newest_build = datetime(2000, 1, 1), None
    for f in WATCH_DIR.iterdir():
        date_m = re.search(FILE_REGEX, f.name)
        if not date_m:
            logger.debug('no date found for %s', f.name)
            continue
        d = parse(date_m.groups()[0])
        if d > newest_build[0]:
            logger.debug('%s with date %s is currently the newest site', f.name, d)
            newest_build = d, f
        else:
            logger.debug('%s with date %s is not the newest site', f.name, d)

    build_ref = newest_build[1]
    if build_ref is None:
        logger.debug('no zipped sites found')
        return False
    UNPACK_DIR.mkdir(parents=True, exist_ok=True)
    build_ref_file = UNPACK_DIR / 'build.txt'
    if build_ref_file.exists():
        logger.debug("build ref exists, checking if it's newer")
        with build_ref_file.open() as f:
            build_ref_existing = f.read()
        if build_ref.name == build_ref_existing:
            logger.debug('current site is based on the newest zip: %s, no extracting', build_ref_existing)
            return False
        else:
            logger.debug('current site older than the newest zip: %s vs %s', build_ref_existing, build_ref.name)

    logger.info('Extracting new site from: %s', build_ref.name)

    for fp in UNPACK_DIR.iterdir():
        fp = fp.resolve()
        if fp.is_file():
            logger.debug('deleting file %s', fp.path)
            os.unlink(fp.path)
        elif fp.is_dir():
            logger.debug('deleting directory %s', fp.path)
            shutil.rmtree(fp.path)

    with build_ref_file.open('w') as f:
        f.write(build_ref.name)
    with ZipFile(build_ref.absolute().path, 'r') as zf:
        zf.extractall(UNPACK_DIR.path)
    return True


class EventHandler(RegexMatchingEventHandler):
    def __init__(self):
        super().__init__(regexes=[FILE_REGEX])

    def on_created(self, event):
        if not event.is_directory:
            logger.info('new file created: %s', event.src_path)
            start = time()
            if build():
                logger.info('New site built in %0.2fs', time() - start)


def main():
    logger.info('Initialising watch to check %s every %d seconds', WATCH_DIR.path, SLEEP_DURATION)
    if not WATCH_DIR.exists():
        raise RuntimeError('watch directory %s does not exist' % WATCH_DIR.path)

    observer = Observer()
    event_handler = EventHandler()
    observer.schedule(event_handler, WATCH_DIR.path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
