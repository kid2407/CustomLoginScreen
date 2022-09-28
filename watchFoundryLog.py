import json
import time
import argparse
from os.path import isfile


def follow(the_file):
    the_file.seek(0, 2)
    while True:
        file_line = the_file.readline()
        if not file_line:
            time.sleep(0.1)
            continue
        yield file_line


def load_available_style_sheets():
    # TODO Load and save available sheets with their respective worlds
    pass


def exchange_sheet():
    # TODO Load files, merge them together and replace the original in the Foundry files as needed
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser("watchFoundryLog.py")
    parser.add_argument("file_name", help="The path of the log file where nginx logs the requests we are interested in. Use \"reset\" to put the original style back in place.", type=str)
    args = parser.parse_args()

    if args.file_name == "reset":
        pass
        # TODO Move original file back to it's place, if it isn't there already
    else:
        target_file = args.file_name

        if not isfile(target_file):
            print("The file \"" + target_file + "\" does not exist!")
            exit()

        logfile = open(target_file, "rt")
        print("Watching the file " + args.file_name + " for relevant data.")
        log_lines = follow(logfile)
        for line in log_lines:
            as_json: dict = json.loads(line)
            print(as_json)
            if "action" in as_json and as_json["action"] == "launchWorld":
                print("Now launching world \"" + as_json["world"] + "\"")
