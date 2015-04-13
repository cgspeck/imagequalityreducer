import os

class FileWrangler(object):
    """docstring for FileWrangler"""
    def __init__(self, directory, max_size_bytes, file_extensions=('jpg', 'png', 'bmp')):
        super(FileWrangler, self).__init__()
        self.directory = directory
        self.max_size_bytes = max_size_bytes
        self.file_extensions = file_extensions

    def get_files(self):
        large_file_list = []
        full_file_list = []

        for root, dirs, files in os.walk(self.directory):
            for f_name in files:
                file_path = os.path.join(root, f_name)
                if file_path.endswith(self.file_extensions):
                    full_file_list.append(file_path)

        print('{count} files found'.format(count=len(full_file_list)))

        for f_name in full_file_list:
            if os.path.getsize(f_name) > self.max_size_bytes:
                large_file_list.append(f_name)

        print('{count} files larger then {size:,} bytes found'.format(
            count=len(large_file_list), size=self.max_size_bytes))
        return large_file_list
