import argparse
import os
import multiprocessing

from RawProcessing import RawProcessing

default_settings = dict(
    film_type = 3, # 0 - B/W, 1 - color negative, 2 - slide, 3 - crop only
    dark_threshold = 0,
    light_threshold = 85,
    border_crop = 1,
    ignore_border = (1, 1),
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
    dust_threshold = 10,
    max_dust_area = 4,
    dust_iter = 5,
    filetype = 'TIFF',
    tiff_compression = 1,
    convert_bw = False,
    rotation = 2, # 0 - no rotation, 1 - 90 counterclockwise, 2 - 180, 3 - 90 clockwise
    iterative_crop = True,
    skip_wrong_crop = False,
    min_crop_ratio = 0.85,
    max_crop_ratio = 0.90
)

presets = {
    'standard': {
        'film_type': 3,
        'rotation': 2
    },
    'b/w_auto': {
        'film_type': 0,
        'border_crop': 3,
        'rotation': 2,
        'ignore_border': (3, 3),
        'skip_wrong_crop': True,
        'filetype': 'JPG',
        'remove_dust': True
    }
}

# Function to create new filename
def replace_extension_with_jpg(file_path):
    base_name, _ = os.path.splitext(file_path)
    return f"{base_name}"


def process_file(params):
    filename, source, target, settings = params
    file = os.path.join(source, filename)
    print(f"Processing file: {file}")
    photo = RawProcessing(file_directory=file, default_settings=settings, global_settings=settings, config_path=None)

    for key in ['filetype', 'tiff_compression', 'dust_threshold', 'max_dust_area', 'dust_iter', 'ignore_border']:
        photo.class_parameters[key] = settings[key]

    photo.load(full_res=True)
    photo.process(full_res=True)
    base_name, _ = os.path.splitext(filename)
    photo.export(os.path.join(target, base_name))

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to the source dir")
    parser.add_argument("target", help="Path to the target dir")
    parser.add_argument("--preset", help=f"{list(presets.keys())}")

    for key, value  in default_settings.items():
        if type(value) == bool:
            parser.add_argument(f"--{key}", action=argparse.BooleanOptionalAction)
        else:
            parser.add_argument(f"--{key}", type=type(value))

    args = parser.parse_args()
    defined_args = {k:v for k,v in args._get_kwargs() if v is not None and k not in {'source', 'target'}}

    preset = defined_args['preset']
    if preset is not None:
        defined_args = defined_args | presets[preset]

    # merge settings
    default_settings = default_settings | defined_args

    with multiprocessing.Manager() as manager:
        with multiprocessing.Pool(4) as pool:
            for dirpath, dirnames, filenames in os.walk(args.source):
                params = [[f, dirpath, args.target, default_settings] for f in sorted(filenames)]
                pool.map(process_file, params)
