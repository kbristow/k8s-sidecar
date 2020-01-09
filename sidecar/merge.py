import os

from ruamel import yaml


def _merge_yaml(default_target_dir, dest_dir, updated_filename):
    print(
        f"Looking for merge hooks:\n\tdefault_target_dir - {default_target_dir}\n\tdest_dir - {dest_dir}\n\tupdated"
        f"-filename - {updated_filename}")
    # merge string in the format base1,base2>output1:path.for.rule=merge,path.for.rule2=overwrite;base3,base4>output2
    full_merge_string = os.getenv("MERGE_YAML")
    if full_merge_string is not None:
        merge_strings = full_merge_string.split(";")
        for merge_string in merge_strings:
            if len(merge_string) != 0:
                base_files = merge_string.split(">")[0].split(",")
                output_base = merge_string.split(">")[1].split(":")
                out_file = output_base[0]
                rules = []
                if len(output_base) > 1:
                    for rule in output_base[1].split(","):
                        rules.append(
                            {"path": rule.split("=")[0], "action": rule.split("=")[1]}
                        )

                # Only merge if the file that was updated is one of the base yaml files
                if updated_filename in base_files:
                    all_file_objects = []
                    for file in base_files:
                        if "/" not in file:
                            file = os.path.join(dest_dir, file)
                        if os.path.isfile(file):
                            with open(file, "r") as fh:
                                all_file_objects.append(yaml.round_trip_load(fh.read(), preserve_quotes=True))

                    output = all_file_objects[0]
                    for index in range(1, len(all_file_objects)):
                        output = merge(output, all_file_objects[index], rules, None)
                    if "/" not in out_file:
                        out_file = os.path.join(default_target_dir, out_file)
                    with open(out_file, "w") as fh:
                        fh.write(yaml.round_trip_dump(output))
                        return True
    print("No merge hook found for modified file. Skipping.")
    return False


def merge(a, b, rules, path=None):
    if path is None:
        path = []
    for key in set(a.keys()).union(b.keys()):
        if key in a and key in b:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], rules, path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                full_path = ".".join(path + [str(key)])
                found_rule = False
                for rule in rules:
                    if rule["path"] == full_path:
                        found_rule = True
                        if rule["action"] == "merge":
                            for index in range(0, len(b[key])):
                                if b[key][index] not in a[key]:
                                    a[key].append(b[key][index])
                        else:
                            a[key] = b[key]
                        break
                if not found_rule:
                    a[key] = b[key]
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