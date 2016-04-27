#!/usr/bin/env python3

import os
import re
import logging
import shutil
from datetime import datetime
from pathlib import Path
from time import sleep, time
from zipfile import ZipFile

logger = logging.getLogger('watch')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(message)s')

fh = logging.FileHandler('watch.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

SLEEP_DURATION = 5
UNPACK_DIR = Path('/var/www/html')
WATCH_DIR = Path('/home/bob/')


def build():
    if not WATCH_DIR.exists():
        logger.debug('watch directory %s does not exist', WATCH_DIR.path)
        return False
    newest_build = datetime(2000, 1, 1), None
    for f in WATCH_DIR.iterdir():
        date_m = re.search('(\d{4}.*?)\.zip$', f.name)
        if not date_m:
            logger.debug('no date found for %s', f.name)
            continue
        d = datetime.strptime(date_m.groups()[0], '%Y-%m-%dT%H:%M:%S.%f')
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


def main():
    logger.info('Initialising watch to check %s every %d seconds', WATCH_DIR.path, SLEEP_DURATION)
    if not WATCH_DIR.exists():
        raise RuntimeError('watch directory %s does not exist' % WATCH_DIR.path)
    while True:
        start = time()
        if build():
            logger.info('New site built in %0.2fs', time() - start)
        sleep(SLEEP_DURATION)

if __name__ == '__main__':
    main()
