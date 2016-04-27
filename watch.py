#!/usr/bin/env python3

# TODO send error emails, delete extra files
import os
import sys
import re
import logging
import shutil
from datetime import datetime
from pathlib import Path
from time import sleep, time
from zipfile import ZipFile

from dateutil.parser import parse
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logger = logging.getLogger('watch')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)

UNPACK_DIR = Path('/var/www/html')
WATCH_DIR = Path('/home/bob/')
FAILED = False


def build():
    newest_build = datetime(2000, 1, 1), None
    for f in WATCH_DIR.iterdir():
        date_m = re.search(r'(\d{4}.*?)\.zip$', f.name)
        if not date_m:
            continue
        d = parse(date_m.groups()[0])
        if d > newest_build[0]:
            newest_build = d, f

    build_ref = newest_build[1].absolute()
    if build_ref is None:
        return False

    UNPACK_DIR.mkdir(parents=True, exist_ok=True)
    build_ref_file = UNPACK_DIR / 'build.txt'
    if build_ref_file.exists():
        with build_ref_file.open() as f:
            build_ref_existing = f.read()
        if build_ref.name == build_ref_existing:
            return False

    logger.info('deploying site %s, deleting old files and waiting for download to complete...', build_ref.name)

    for fp in UNPACK_DIR.iterdir():
        fp = fp.resolve()
        if fp.is_file():
            os.unlink(fp.path)
        elif fp.is_dir():
            shutil.rmtree(fp.path)

    with build_ref_file.open('w') as f:
        f.write(build_ref.name)

    # we have to make sure the file isn't still being written
    while True:
        size = build_ref.stat().st_size
        sleep(0.1)
        if size == build_ref.stat().st_size:
            # file size hasn't change for 0.1 second, must be stable
            break

    logger.info('Extracting new site from: %s, size: %s', build_ref.name, file_size(size))

    with ZipFile(build_ref.absolute().path, 'r') as zf:
        zf.extractall(UNPACK_DIR.path)
    return True


def file_size(num):
    for unit in ['', 'K', 'M', 'G', 'T']:
        if abs(num) < 1024.0:
            return '%3.1f%sB' % (num, unit)
        num /= 1024.0


class EventHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=['*.zip'])

    def on_created(self, event):
        if not event.is_directory:
            logger.info('new file created: %s', event.src_path)
            start = time()
            try:
                new_build = build()
            except:
                global FAILED
                FAILED = True
                raise
            else:
                if new_build:
                    logger.info('New site built in %0.2fs', time() - start)


def main():
    logger.info('Initialising watch to check %s', WATCH_DIR.path)
    if not WATCH_DIR.exists():
        raise RuntimeError('watch directory %s does not exist' % WATCH_DIR.path)

    observer = Observer()
    event_handler = EventHandler()
    observer.schedule(event_handler, WATCH_DIR.path, recursive=True)
    observer.start()
    try:
        while not FAILED:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    sys.exit(FAILED)

if __name__ == '__main__':
    main()
