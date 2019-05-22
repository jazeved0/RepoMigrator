import sys
import os
import pexpect

__author__ = "Joseph Azevedo"

"""
migrate.py
----------
TODO write
"""

HELP = """
migrate.py
Usage:
   migrate.py TODO

Options:
  -h --help    Show this help description"""

TEMP_DIR = "temp"
BASE_CLONE_CMD = "git clone {} --bare"


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        help()
    elif len(sys.argv) < 3:
        print("Wrong number of arguments. See usage:")
        help()

    source_repo = sys.argv[1]
    dest_repo   = sys.argv[2]

    try:
        # Create target Directory
        os.mkdir(TEMP_DIR)
        print("Temporary dir {} created ".format(TEMP_DIR))
    except FileExistsError:
        print("Temporary dir {} already exists ".format(TEMP_DIR))

    new_cwd = os.path.join(os.getcwd(), TEMP_DIR)

    command = BASE_CLONE_CMD.format(source_repo)
    process = pexpect.spawn(command, cwd=new_cwd)
    process.timeout = 300
    process.expect(r"Cloning into bare repository '(.+)'...[\n\r]+")
    print(process.match.group(0))
    repo_name = process.match.group(0)

    result = process.expect(['Unpacking objects: [0-9]+% ([0-9]+/[0-9]+), done.', 'fatal: '])
    if result == 0:
        print('Bare clone succeeded')

    elif result == 1:
        print('An error occurred: {}'.format(process.after))
        process.kill(0)
        quit()

    new_cwd = os.path.join(new_cwd, repo_name)


def help():
    # Display help and stop
    print(HELP)
    quit()


# Run script
if __name__ == "__main__":
    main()
