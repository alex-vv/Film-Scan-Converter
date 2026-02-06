import argparse
import os

from RawProcessing import RawProcessing

default_settings = dict(
    film_type = 3,
    dark_threshold = 0,
    light_threshold = 83,
    border_crop = -1,
    flip = True,
    white_point = 0,
    black_point = 0,
    gamma = 0,
    shadows = 0,
    highlights = 0,
    temp = 0,
    tint = 0,
    sat = 100,
    base_detect = 0,
    base_rgb = (255, 255, 255),
    remove_dust = False,
    filetype = 'TIFF',
    tiff_compression = 1 
)

# Function to create new filename
def replace_extension_with_jpg(file_path):
    base_name, _ = os.path.splitext(file_path)
    return f"{base_name}"


def process_file(filename, source, target):
    file = os.path.join(source, filename)
    print(f"Processing file: {file}")
    photo = RawProcessing(file_directory=file, default_settings=default_settings, global_settings=default_settings, config_path=None)
    photo.class_parameters['filetype'] = default_settings['filetype']
    photo.class_parameters['tiff_compression'] = default_settings['tiff_compression']
    photo.load(full_res=True)
    photo.process(full_res=True)
    base_name, _ = os.path.splitext(filename)
    photo.export(os.path.join(target, base_name))

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to the source dir")
    parser.add_argument("target", help="Path to the target dir")
    args = parser.parse_args()

    for dirpath, dirnames, filenames in os.walk(args.source):
        for filename in filenames:
            process_file(filename, dirpath, args.target)
