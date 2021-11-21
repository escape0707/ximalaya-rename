import json
import pathlib


def prompt_for_user_confirmation(request_text: str) -> bool:
    user_input = input(request_text + " [Y/n] ")
    return user_input in ("", "Y", "y")


def parse_json_info(
    json_file_collection: list[pathlib.Path] = list(pathlib.Path().glob("*list.json")),
) -> list[tuple[pathlib.Path, pathlib.Path]]:
    ret: list[tuple[pathlib.Path, pathlib.Path]] = []
    for json_file in json_file_collection:
        with json_file.open("rb") as f:
            track_info_collection = json.load(f)
            if type(track_info_collection) is not list:
                raise TypeError(
                    "The JSON file given to parese is not a list info file. Did you send in a album info file instead?"
                )
            for track_info in track_info_collection:
                try:
                    albumId = track_info["albumId"]
                    assert type(albumId) is int
                    albumTitle = track_info["albumTitle"]
                    assert type(albumTitle) is str
                    title = track_info["title"]
                    assert type(title) is str
                    trackId = track_info["trackId"]
                    assert type(trackId) is int
                except KeyError:
                    raise
                track_dir = json_file.with_name(str(albumId))
                track_new_dir = track_dir.with_name(f"{albumId}-{albumTitle}")
                track_name = pathlib.Path(f"{trackId}.m4a")
                track_new_name = track_name.with_stem(f"{trackId}-{title}")
                ret.append((track_dir / track_name, track_new_dir / track_new_name))
    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='A simple script to rename (actually, create "hardlink") cached Ximalaya audio files according to related JSON info, assuming audio files folder is placed next to the JSON file.'
    )
    parser.add_argument(
        "json_files",
        nargs="*",
        default=list(pathlib.Path().glob("*list.json")),
        help='JSON files to parse. Use glob (e.g. /path/to/dir/*list.json) to point to a series of files. (Default: all files matching glob "./*list.json"',
    )
    cli_args = parser.parse_args()
    print(cli_args.json_files)

    rename_path_pair_collection = parse_json_info(cli_args.json_files)
    print("Original file location\t\t\tNew hardlink location:")
    for origin, new in rename_path_pair_collection:
        print(f"{origin}\t{new}")
    if prompt_for_user_confirmation("Start creating new hardlink?"):
        for origin, new in rename_path_pair_collection:
            new.parent.mkdir(parents=True, exist_ok=True)
            # Should be `new.hardlink_to(origin)` since Python 3.10
            origin.link_to(new)
