#!/usr/bin/env python3

# TODO send error emails
import os
import logging
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from time import time
from zipfile import ZipFile

import pyinotify

logger = logging.getLogger('watch')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)

UNPACK_DIR = Path('/var/www/html').absolute()
WATCH_DIR = Path('/home/bob/').absolute()
WATCH_FILE = 'site.zip'
WATCH_PATH = WATCH_DIR / WATCH_FILE
BUILD_REF_FILE = UNPACK_DIR / 'build.txt'


class Builder:
    last_file_hash = None

    def handle_change(self, event):
        if event.pathname != WATCH_PATH.path:
            return
        logger.info('%s changed, deploying...', WATCH_FILE)
        self.build()

    def build(self):
        start = time()
        file_hash = self.md5_hash(WATCH_PATH)
        if file_hash == self.last_file_hash:
            logger.info('file unchanged, not building')
            return
        self.last_file_hash = file_hash
        file_size = self.format_file_size(WATCH_PATH.stat().st_size)
        with ZipFile(WATCH_PATH.path, 'r') as zf:
            file_count = len(zf.namelist())

        logger.info('zip file ok, %d files, size: %s, hash: %s, deleting old site...', file_count, file_size, file_hash)

        UNPACK_DIR.mkdir(parents=True, exist_ok=True)
        for fp in UNPACK_DIR.iterdir():
            fp = fp.resolve()
            if fp.is_file():
                os.unlink(fp.path)
            elif fp.is_dir():
                shutil.rmtree(fp.path)

        with BUILD_REF_FILE.open('w') as f:
            f.write('deploy\ntimestamp: {}\nzip size: {}\nfiles: {}\nhash: {}'
                    '\n'.format(datetime.now(), file_size, file_count, file_hash))

        with ZipFile(WATCH_PATH.absolute().path, 'r') as zf:
            zf.extractall(UNPACK_DIR.path)
        logger.info('New site built in %0.2fs', time() - start)

    @staticmethod
    def md5_hash(file_path):
        hash_md5 = hashlib.md5()
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def format_file_size(num):
        for unit in ['', 'K', 'M', 'G', 'T']:
            if abs(num) < 1024.0:
                return '%3.1f%sB' % (num, unit)
            num /= 1024.0


def main():
    logger.info('Initialising watch to check %s', WATCH_DIR.path)
    if not WATCH_DIR.exists():
        raise RuntimeError('watch directory %s does not exist' % WATCH_DIR.path)
    builder = Builder()
    if WATCH_PATH.exists():
        logger.info('%s exists, building...', WATCH_FILE)
        builder.build()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, builder.handle_change)
    wm.add_watch(WATCH_DIR.path, pyinotify.IN_CLOSE_WRITE)
    notifier.loop()

if __name__ == '__main__':
    main()
