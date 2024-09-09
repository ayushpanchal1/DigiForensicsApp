
import os
import math
from PIL import Image
import mmap


class FileReader(object):
    def __init__(self, path):
        self.path = path
        self.length = os.path.getsize(path)

    def __len__(self):
        return self.length

    def read_chunk(self, offset, size):
        """Reads a chunk of the file using memory mapping for faster access."""
        with open(self.path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                mm.seek(offset)
                return mm.read(size)


def choose_file_dimensions(num_bytes, input_dimensions=None, square=False):
    num_pixels = int(math.ceil(float(num_bytes) / 3.0))
    sqrt_max = int(math.ceil(math.sqrt(num_pixels)))

    if square:
        return sqrt_max, sqrt_max

    if input_dimensions:
        if input_dimensions[0]:  # Width is specified
            return input_dimensions[0], math.ceil(num_pixels / input_dimensions[0])
        if input_dimensions[1]:  # Height is specified
            return math.ceil(num_pixels / input_dimensions[1]), input_dimensions[1]

    best_dimensions = None
    best_extra_bytes = None

    for i in range(sqrt_max, 0, -1):
        dimensions = (i, math.ceil(num_pixels / i))
        extra_bytes = dimensions[0] * dimensions[1] * 3 - num_bytes
        if best_dimensions is None or extra_bytes < best_extra_bytes:
            best_dimensions = dimensions
            best_extra_bytes = extra_bytes

    return best_dimensions


def file_to_png(file_path, output_file, dimensions=None, square=False):
    reader = FileReader(file_path)
    num_bytes = len(reader)
    dimensions = choose_file_dimensions(num_bytes, dimensions, square)
    img = Image.new('RGB', dimensions)
    pixels = img.load()

    offset = 0
    chunk_size = 3 * dimensions[0]
    row = 0

    while offset < num_bytes:
        chunk = reader.read_chunk(offset, chunk_size)
        offset += len(chunk)

        for column in range(0, len(chunk), 3):
            color = [chunk[column], 0, 0]
            if column + 1 < len(chunk):
                color[1] = chunk[column + 1]
            if column + 2 < len(chunk):
                color[2] = chunk[column + 2]

            pixels[column // 3, row] = tuple(color)

        row += 1

    img.save(output_file, format="PNG")


def convert_file_to_image(file_path):
    """Converts a binary file to a PNG image and returns the image path."""
    output_dir = "./image_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{os.path.basename(file_path)}.png")
    file_to_png(file_path, output_file, square=True)
    
    return output_file