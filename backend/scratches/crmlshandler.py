import os
import sys

if os.path.abspath(os.curdir) not in sys.path:
    sys.path.append(os.path.abspath(os.curdir))

from lib.facebookads.crmlsziphandler import CrmlsZipHandler


if __name__ == "__main__":
    print("Ziphandler Usage...")

    config_path = os.path.abspath(os.curdir) + "/config/fbcsv.ini"
    zipfile_path = os.path.abspath(os.curdir) + "/scratches/Full__Photos.zip"
    release_path = os.path.abspath(os.curdir) + "/data/test_release"
    unzip_path = release_path

    crmlszip = CrmlsZipHandler(zipfile_path, config_path, release_path, unzip_path)
    crmlszip.unzip()
    crmlszip.handle()


