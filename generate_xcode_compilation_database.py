#! /usr/bin/env python3

import json
import argparse
import os


script_name = os.path.basename(__file__)


def panic(*args, **kwargs):
    print(*args, **kwargs)
    exit(-1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Generate a compilation database from a -GXcode'd cmake project.\nUse like {script_name} <build dir>"
    )

    parser.add_argument(
        "build_dir", type=str, help="the directory where CompilationDatabase/ resides"
    )
    parser.add_argument(
        "--output",
        help="the directory where compile_commands.json should be written. By default set to build_dir",
    )
    parser.add_argument(
        "--purge-old",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="purge old compile commands from the cache.",
    )

    build_args = parser.add_argument_group("Build before creating cdb")
    build_args.add_argument(
        "--build-with",
        help="first build with the given command before getting the compilation database."
        " Useful if your build config doesn't generate a compilation database."
        " Expects an xcodebuild-able system (or one that respects Xcode's build setting variables)."
        " Adds compilation database generating options automatically."
        f' Invoke like `{script_name} --build-with "xcodebuild <options>"` or `{script_name} --build-with "cmake --build build <options> --"`.'
        " Xcode will not compile a file that has not changed/if build settings are not changed."
        " Due to this, the cdb fragments will also not be generated on every build, and you will be skipping some build"
        " commands in your compile_commands.json if you are relying on this subcommand and run a build externally."
        " Instead of this command, it is suggested that you add `-gen-cdb-fragment-path CompilationDatabase` to your compilation commands through your build system."
        " This is done by default in the provided CMakeLists.txt file.",
    )
    build_args.add_argument(
        "--ignore-build-errors",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="ignore build errors and generate cdb. Useful to get the compile errors into your editor through the LSP. Default is False.",
    )

    args = parser.parse_args()
    if args.output is None:
        args.output = args.build_dir
    return args


# print(args)


def get_cdb_lisiting(args: argparse.Namespace) -> list[str]:
    dir_name = args.build_dir + "/CompilationDatabase"
    dirlist = list(map(lambda x: f"{dir_name}/{x}", os.listdir(dir_name)))
    return dirlist


def build_xcode(args):
    if args.build_with is not None:
        if "OTHER_CFLAGS" in args.build_with:
            panic(
                f"Error: OTHER_CFLAGS is not supported as a build option as it will be overriden by {script_name}. Exiting."
            )
    exit_code = os.system(
        f'cd {args.build_dir} && {args.build_with} OTHER_CFLAGS="\$(inherited) -gen-cdb-fragment-path {args.build_dir}/CompilationDatabase"'
    )
    if exit_code != 0:
        if args.ignore_build_errors == False:
            panic(f"Error: Build process failed. Stopping {script_name}.")
        else:
            print("Warning: Build process failed. Continuing...")


def main():
    args = parse_arguments()
    if args.build_with is not None:
        build_xcode(args)

    try:
        dirlist = get_cdb_lisiting(args)
    except FileNotFoundError:
        panic(
            "Error: The directory %s/CompilationDatabase/ does not exist."
            % args.build_dir
        )

    if len(dirlist) == 0:
        panic("Error: The directory %s/CompilationDatabase/ is empty." % args.build_dir)

    # Keys: Files that are being compiled, taken from each partial db
    # Values: A list of ordered pairs.
    #         First element is the modification time of the second element.
    #         Second element is the path to the partial db in question
    partial_cdbs_for_sorting = dict()
    for filename in dirlist:
        if not filename.endswith(".json"):
            panic(
                "Error: found file without extension .json in CompilationDatabase/ (%s)"
                % filename
            )
        print(f"Processing cdb fragment {filename}")
        with open(filename, "rb") as f:
            partial_cdb = f.read()
        try:
            # every partial cdb contains a ",\n" at the end of it.
            # remove ",\n" from the end of partial_cdb before loading
            partial_cdb_parsed = json.loads(partial_cdb[:-2])
        except json.decoder.JSONDecodeError:
            print("Warning: Could not JSON decode %s. Skipping this file." % filename)
            continue

        if partial_cdb_parsed["file"] not in partial_cdbs_for_sorting:
            partial_cdbs_for_sorting[partial_cdb_parsed["file"]] = []

        partial_cdbs_for_sorting[partial_cdb_parsed["file"]].append(
            (os.path.getmtime(filename), filename)
        )

    for compiled_file_path in partial_cdbs_for_sorting:
        # mtime, partial_cdb = partial_cdbs[compiled_file_path]
        partial_cdbs_for_sorting[compiled_file_path] = sorted(
            partial_cdbs_for_sorting[compiled_file_path],
            key=lambda x: x[0],
            reverse=True,
        )

    if args.purge_old:
        for compiled_file_path in partial_cdbs_for_sorting:
            # the first one in the list is the most recent compilation command
            files_to_purged = partial_cdbs_for_sorting[compiled_file_path][1:]
            for mtime, partial_cdb_path in files_to_purged:
                print(f"Purging old cdb fragment {partial_cdb_path}")
                os.remove(partial_cdb_path)

    # [0] for the first element (the latest partial cdb that compiled a given file)
    # [0] is of type (mtime, partial_cdb_path)
    # [1] gets partial_cdb_path
    partial_cdbs = map(lambda x: x[0][1], partial_cdbs_for_sorting.values())

    # print(partial_cdbs)

    with open(args.output + "/compile_commands.json", "wb") as cdb:
        cdb.write(b"[\n")
        for partial_cdb_path in partial_cdbs:
            with open(partial_cdb_path, "rb") as partial_cdb:
                cdb.write(partial_cdb.read())
        # end is ",\n"
        cdb.seek(-2, os.SEEK_END)
        cdb.write(b"\n]\n")

    print(
        "Successfully saved compilation database at %s"
        % (args.output + "/compile_commands.json")
    )


if __name__ == "__main__":
    main()
