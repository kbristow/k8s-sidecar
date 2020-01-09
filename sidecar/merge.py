import os
from functools import reduce

from ruamel import yaml


def _merge_yaml(default_target_dir, dest_dir, updated_filename):
    # merge string in the format base1,base2>output1;base3,base4>output2
    full_merge_string = os.getenv("MERGE_YAML")
    if full_merge_string is not None:
        merge_strings = full_merge_string.split(";")
        for merge_string in merge_strings:
            if len(merge_string) != 0:
                base_files = merge_string.split(">")[0].split(",")
                out_file = merge_string.split(">")[1]

                # Only merge if the file that was updated is one of the base yaml files
                if updated_filename in base_files:
                    all_file_objects = []
                    for file in base_files:
                        if "/" not in file:
                            file = os.path.join(dest_dir, file)
                        if os.path.isfile(file):
                            with open(file, "r") as fh:
                                all_file_objects.append(yaml.round_trip_load(fh.read(), preserve_quotes=True))

                    output = reduce(merge, all_file_objects)
                    if "/" not in out_file:
                        out_file = os.path.join(default_target_dir, out_file)
                    with open(out_file, "w") as fh:
                        fh.write(yaml.round_trip_dump(output))


def merge(a, b, path=None):
    if path is None: path = []
    for key in set(a.keys()).union(b.keys()):
        if key in a and key in b:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        elif key in b:
            a[key] = b[key]
        else:
            pass
    return a


def merge_hooks(default_target_dir, dest_dir, updated_filename):
    _merge_yaml(default_target_dir, dest_dir, updated_filename)
