import argparse
import os
import multiprocessing

from RawProcessing import RawProcessing

default_settings = dict(
    film_type = 3,
    dark_threshold = 0,
    light_threshold = 85,
    border_crop = 1,
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
    tiff_compression = 1,
    convert_bw = False,
    rotation = 0,
    iterative_crop = True,
    min_crop_ratio = 0.85,
    max_crop_ratio = 0.90
)

# Function to create new filename
def replace_extension_with_jpg(file_path):
    base_name, _ = os.path.splitext(file_path)
    return f"{base_name}"


def process_file(params):
    filename, source, target, settings = params
    file = os.path.join(source, filename)
    print(f"Processing file: {file}")
    photo = RawProcessing(file_directory=file, default_settings=settings, global_settings=settings, config_path=None)
    photo.class_parameters['filetype'] = settings['filetype']
    photo.class_parameters['tiff_compression'] = settings['tiff_compression']
    photo.load(full_res=True)
    photo.process(full_res=True)
    base_name, _ = os.path.splitext(filename)
    photo.export(os.path.join(target, base_name))

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to the source dir")
    parser.add_argument("target", help="Path to the target dir")
    parser.add_argument("--film_type", type=int, help="0 - B/W, 1 - color negative, 2 - slide, 3 - crop only")
    parser.add_argument("--filetype",  help="JPG/TIFF")
    parser.add_argument("--border_crop", type=int, help="border crop (can be negative)")
    parser.add_argument("--convert_bw", action=argparse.BooleanOptionalAction, help="Convert to B/W")
    parser.add_argument("--rotation", type=int, help="0 - no rotation, 1 - 90 counterclockwise, 2 - 180, 3 - 90 clockwise")
    args = parser.parse_args()
    defined_args = {k:v for k,v in args._get_kwargs() if v is not None and k not in {'source', 'target'}}

    # merge settings
    default_settings = default_settings | defined_args

    #for dirpath, dirnames, filenames in os.walk(args.source):
    #    for filename in filenames:
    #        process_file([filename, dirpath, args.target, default_settings])

    with multiprocessing.Manager() as manager:
        with multiprocessing.Pool(4) as pool:
            for dirpath, dirnames, filenames in os.walk(args.source):
                params = [[f, dirpath, args.target, default_settings] for f in sorted(filenames)]
                pool.map(process_file, params)
