from io import BytesIO
from os import path

from PIL import Image

class QualityReducer(object):
    """docstring for QualityReducer"""
    quality_range = {
        'PNG': {
            'min_val': 1,
            'max_val': 9,
            'meta': 'compress_level',
            'smallest': 9
        },
        'JPEG': {
            'min_val': 1,
            'max_val': 100,
            'meta': 'quality',
            'smallest': 1
        }
    }

    def __init__(self, max_size_bytes):
        super(QualityReducer, self).__init__()
        self.target_size = max_size_bytes
        # name of last file we ran over
        self.last_run = None
        # set by the load method
        self.original_filename = None
        self.original_format = None
        self.original_image = None
        # set by the find me a quality method
        self.previous_memfile = None
        self.previous_quality = None
        self.previous_size = None

    def load(self, filename):
        """
        Opens filename and records filename, type, size etc
        """
        self.original_filename = filename
        self.original_image = Image.open(filename)
        self.original_format = self.original_image.format
        self.original_size = path.getsize(filename)

    def find_optimum_quality(self):
        """
        Loops through different quality levels until it can find a cloest match to target_size
        """
        if self.last_run == self.original_filename:
            return

        if not self.original_filename:
            raise ValueError('Must set a file to open')

        if self.original_size < self.target_size:
            raise ValueError('Original file is less than target size')

        quality_spec = self.quality_range[self.original_format]
        x = int(quality_spec['max_val']/2)
        new_x = None
        upper_limit = quality_spec['max_val']
        lower_limit = quality_spec['min_val']

        while True:
            data, size = self._simulate_save(x)

            if size < self.target_size:
                if quality_spec['smallest'] == quality_spec['max_val']:
                    if lower_limit < x:
                        upper_limit = x
                        new_x = int((x - lower_limit) / 2) + lower_limit
                else:
                    # go up half a block
                    if upper_limit > x:
                        lower_limit = x
                        new_x = int((upper_limit - x) / 2) + x

            if size > self.target_size:
                if quality_spec['smallest'] == quality_spec['max_val']:
                    if upper_limit > x:
                        lower_limit = x
                        new_x = int((upper_limit - x) / 2) + x
                else:
                    # go down half a block
                    if lower_limit < x:
                        upper_limit = x
                        new_x = int((x - lower_limit) / 2) + lower_limit

            if new_x != x:
                # there's more compressing to do!
                self.previous_memfile = data
                self.previous_quality = x
                self.previous_size = size
                x = new_x
                continue

            # x cannot go anywhere, so make a selection
            chosen_size = self._select_closest(size, self.previous_size)

            if chosen_size == size:
                # update previous_memfile etc one last time
                self.previous_memfile = data
                self.previous_quality = x
                self.previous_size = size

            break

        print('Selected quality level %s with size %s' % (self.previous_quality, self.previous_size))

    def _select_closest(self, size1, size2):
        """
        Compares size1 and size2 against target_size and returns the closest
        """
        abs_diff_1 = abs(self.target_size - size1)
        abs_diff_2 = abs(self.target_size - size2)
        selection = None

        if abs_diff_1 < abs_diff_2:
            selection = size1
        else:
            selection = size2
        print('Selecting %s from %s and %s' % (selection, size1, size2))
        return selection

    def _simulate_save(self, quality):
        """
        Saves original_image to stream IO at given quality and returns the data and size
        """
        output = BytesIO()
        save_kwargs = {
            'format': self.original_format,
            self.quality_range[self.original_format]['meta']: quality
        }
        self.original_image.save(
            output,
            **save_kwargs
        )
        print('Simulated save level %s size %s bytes' % (quality, output.getbuffer().nbytes))
        return output, output.getbuffer().nbytes

    def save(self, filename=None):
        """
        Saves compressed version
        """
        if not filename:
            raise

        if self.last_run != self.original_filename:
            self.find_optimum_quality()

        buf = self.previous_memfile
        buf.seek(0)
        with open(filename, 'wb') as fd:
            t = buf.read(1048576)
            while t:
                fd.write(t)
                t = buf.read(1048576)
