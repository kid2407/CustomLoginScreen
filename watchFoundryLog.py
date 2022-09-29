import json
import os
import time
import argparse
from os.path import isfile, isdir
from shutil import copyfile, copyfileobj
from typing import Generator, Any, TextIO


def setup() -> tuple[str, str, str, dict[str, str]]:
    parser = argparse.ArgumentParser("watchFoundryLog.py")
    parser.add_argument("log_file_path",
                        help="The path of the log file where nginx logs the requests we are interested in. Use "
                             "\"reset\" to put the original style back in place.",
                        type=str)
    parser.add_argument("foundry_path", help="The path to the root of your foundry install.", type=str)
    args = parser.parse_args()

    foundry_dir = args.foundry_path
    if not foundry_dir.endswith(os.sep):
        foundry_dir += os.sep

    target_file = "{}app{}resources{}app{}public{}css{}style.css".format(foundry_dir, os.sep, os.sep,
                                                                         os.sep, os.sep, os.sep)

    log_file_path = args.log_file_path
    if log_file_path != "reset" and not isfile(log_file_path):
        print("The file \"" + log_file_path + "\" does not exist!")
        exit(1)

    if not isfile(target_file):
        print("Could not load original style.css ({}): file does not exist or is unreadable.".format(target_file))
        exit(1)

    if not isfile("original.css"):
        copyfile(target_file, "original.css")

    sheets_dir_path = os.curdir + os.sep + "styles"
    sheets = load_available_style_sheets(sheets_dir_path)

    return args.log_file_path, foundry_dir, target_file, sheets


def follow(the_file: TextIO) -> Generator[Any, Any, None]:
    """
    Look at the file waiting for new lines to be added
    """
    the_file.seek(0, 2)
    while True:
        file_line = the_file.readline()
        if not file_line:
            time.sleep(0.1)
            continue
        yield file_line


def load_available_style_sheets(sheets_dir: str) -> dict[str, str]:
    """
    Loads the available style sheets, if any are available and saves them to a dict with the file name as the key
    """
    sheets = {}

    if not isdir(sheets_dir):
        os.mkdir(sheets_dir)

    for file in os.listdir(sheets_dir):
        file_path, file_extension = os.path.splitext(file)
        if file_extension == ".css":
            css_file_name = os.path.basename(file_path)
            sheets[css_file_name] = os.path.abspath(sheets_dir + os.sep + file)
            print("Loaded sheet for world \"{}\".".format(css_file_name))

    return sheets


def exchange_sheet(world: str, sheet_dict: dict[str, str]):
    """
    Update the style.css for the specified world, if None reset to default
    """

    target = open(target_file_path, 'wt')
    copyfileobj(open("original.css", 'rt'), target)
    if world not in sheet_dict:
        print("Style sheet for world \"{}\" does not exist. Using default sheet.".format(world))
    else:
        sheet_path = sheet_dict[world]
        copyfileobj(open(sheet_path, 'rt'), target)
    target.close()
    print("Updated style.css for world \"{}\".".format(world))


if __name__ == '__main__':
    log_file, foundry_path, target_file_path, sheet_list = setup()

    if log_file == "reset":
        copyfile("original.css", target_file_path)
        print("Replaced style.css with the original.")
    else:
        logfile = open(log_file, "rt")
        print("Watching the file " + log_file + " for relevant data.")
        log_lines = follow(logfile)
        for line in log_lines:
            as_json: dict = json.loads(line)
            if "action" in as_json and as_json["action"] == "launchWorld":
                world_name = as_json["world"]
                print("Now launching world \"" + as_json["world"] + "\"")
                exchange_sheet(world=world_name, sheet_dict=sheet_list)
