import argparse
import os
import sys

from .qualityreducer import QualityReducer
from .filewrangler import FileWrangler

class UtilRunner(object):
    """Scan specified folder or file and run quality reducer against it"""
    def __init__(self):
        super(UtilRunner, self).__init__()
        self.qr = QualityReducer()
        self.fr = FileWrangler()


class ReadableDir(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ReadableDir, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def main():
    parser = argparse.ArgumentParser(
        description="Image compression quality reducer"
    )
    parser.add_argument(
        "-s", "--size", help="Target file size in kilobytes", default=256, action="store"
    )
    parser.add_argument(
        "-o", "--overwrite", help="Overwrite original files", action="store_true"
    )
    parser.add_argument(
        "directory", help="Folder to run reducer over",
        action=ReadableDir, nargs=1
    )
    args = parser.parse_args()
    max_size_bytes = args.size * 1000
    fr = FileWrangler(directory=args.directory, max_size_bytes=max_size_bytes)
    file_list = fr.get_files()

    if len(file_list) == 0:
        sys.exit(0)

    qr = QualityReducer(max_size_bytes=max_size_bytes)

    for f_name in file_list:
        print('Loading {0}'.format(f_name))
        qr.load(f_name)

        if args.overwrite:
            print('Saving over original')
            qr.save(f_name)
        else:
            new_file_name = '{pre}_reduced.{extension}'.format(
                pre=''.join(f_name.split('.')[:1]), extension=''.join(f_name.split('.')[1:]))
            print('Saving to {0}'.format(new_file_name))
            qr.save(new_file_name)

if __name__ == "__main__":
    main()
