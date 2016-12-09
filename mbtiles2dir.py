import argparse
import errno
import logging
import os
import sqlite3
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main():
    parser = argparse.ArgumentParser(description='Dumps an mbtiles file to files in directories.')
    parser.add_argument('mbtiles', type=argparse.FileType('r'),
                        help='the input mbtiles file')
    parser.add_argument('prefix',
                        help='prefix directory name to write tiles to')

    args = parser.parse_args()

    conn = sqlite3.connect(args.mbtiles.name)
    c = conn.cursor()

    c.execute("select min(zoom_level) as min_z, max(zoom_level) as max_z from tiles")
    (min_z, max_z) = c.fetchone()

    logging.info("Min zoom: %s Max zoom: %s", min_z, max_z)

    c.execute("select value from metadata where name='format'")
    (fmt,) = c.fetchone()

    c.execute("select * from tiles")

    count = 0
    for (z, x, y, data) in c:
        dir_path = "{}/{}/{}".format(args.prefix, z, x)
        filename = "{}.{}".format(y, fmt)
        mkdir_p(dir_path)
        with open(os.path.join(dir_path, filename), 'wb') as f:
            logging.debug("Write out %s bytes to %s/%s.mvt", len(data), dir_path, y)
            f.write(data)
            count += 1

    logging.info("Wrote out %s files", count)

if __name__ == '__main__':
    main()
