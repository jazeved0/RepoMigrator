import os
import pexpect
import argparse
import shutil
from pathlib import Path

__author__ = "Joseph Azevedo"
__version__ = "1.0"

DESCRIPTION = "Migrate github repositories between two different optionally authenticated remotes."
DEFAULT_TEMP_DIR = "temp"
DEFAULT_REMOTE = "public"
DEFAULT_TIMEOUT = 10000


def main(source_repo, dest_repo, source_auth=None, dest_auth=None, temp_dir=None, remote=None, timeout=None):
    """Performs the migration logic from source_repo to dest_repo, creating a temporary directory (if it doesn't
    already exist) and bare cloning into that. Then, the dest repo is added as a remote to the local copy before
    pushing to that remote. Finally, the repo folder is deleted, and if the temporary directory didn't exist before,
    it is also removed.

    :param source_repo: The https path of the source repository
    :param dest_repo:   The https path of the destination repository
    :param source_auth: An optional tuple containing (user, password/token) for the source repo
    :param dest_auth:   An optional tuple containing (user, password/token) for the destination repo
    :param temp_dir:    An optional path to use as the temporary directory to clone repos into (./temp used otherwise)
    :param remote       An optional name for the remote
    :param timeout      Optional ms to wait between git command parses in pexpect
    """
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    temp_path, temp_existed_before = try_create_temp_dir(temp_dir)
    repo_path = clone_bare(source_repo, temp_path, source_auth, timeout=timeout)
    remote_name = add_remote(repo_path, dest_repo, remote)
    push_mirror(repo_path, dest_auth, remote_name, timeout=timeout)

    # Clean up
    try:
        if temp_existed_before:
            shutil.rmtree(repo_path)
        else:
            shutil.rmtree(temp_path)
    except OSError as e:
        print ("An error ocurred in cleanup. Exiting")
        quit()


def clone_bare(source_repo, path, source_auth=None, timeout=DEFAULT_TIMEOUT):
    base_clone_command = """git clone {} --bare"""
    command = base_clone_command.format(source_repo)
    process = pexpect.spawn(command, cwd=path)
    process.timeout = int(timeout)

    # Can fail if not valid
    result = process.expect([r"Cloning into bare repository '(.+)'[.][.][.][\n\r]+", "fatal: "])
    if result == 1:
        error(process)

    # Succeeded
    repo = process.match.group(1).decode("utf-8")
    print("""Attempting to clone repository "{}" """.format(repo))

    # Potential login stage
    success_pattern = r"Unpacking objects: [0-9]+% [(][0-9]+/[0-9]+[)], done[.]"
    if handle_auth(process, success_pattern, source_auth):
        repo_path = (Path(path) / repo).resolve()
        print("""Bare repository successfully cloned into "{}" """.format(repo_path))
        return repo_path
    else:
        return ""


def add_remote(repo_path, remote_repo, remote_name=None):
    """Adds a remote to the given repository"""
    if remote_name is None:
        remote_name = DEFAULT_REMOTE

    base_add_remote_command = """git remote add {} {}"""
    command = base_add_remote_command.format(remote_name, remote_repo)
    process = pexpect.spawn(command, cwd=repo_path)
    
    process.expect(pexpect.EOF)
    process.kill(0)
    print("""Remote "{}" added""".format(remote_name))
    return remote_name


def push_mirror(repo_path, dest_auth, remote_name, timeout=DEFAULT_TIMEOUT):
    """Pushes the repository at the given location to the specified remote as a mirror"""
    base_push_command = """git push {} --mirror"""
    command = base_push_command.format(remote_name)
    process = pexpect.spawn(command, cwd=repo_path)
    process.timeout = int(timeout)

    success_pattern = r"remote: Resolving deltas: [0-9]+% [(][0-9]+/[0-9]+[)], done[.]"
    if handle_auth(process, success_pattern, dest_auth):
        print("""Pushed to remote "{}" """.format(remote_name))


def handle_auth(process, success_pattern, auth=None):
    error_pattern = "fatal: "
    result = process.expect([success_pattern, error_pattern, pexpect.EOF, """Username for '(.+)':"""])
    if result == 3:
        server = process.match.group(1).decode("utf-8")
        # Authentication required
        if auth is not None:
            process.sendline(auth[0])
            process.expect("""Password for '.+':""")
            process.sendline(auth[1])
            print("""Authenticated for repo at "{}" """.format(server))
            result = process.expect([success_pattern, error_pattern, pexpect.EOF])
        else:
            print("Error: Authentication required for \"{}\" but insufficient credentials were supplied"
                .format(server))
            exitScript(process)

    if result == 0:
        process.expect(pexpect.EOF)
        process.kill(0)
        return True
    elif result == 1:
        error(process)
    elif result == 2:
        error(process, at_eof=True)
    return False


def error(process, at_eof=False):
    """Handles a fatal error and closes a pexpect process before terminating the script"""
    error_format = """An unexpected error occurred: "{}" """

    if not at_eof:
        process.expect(pexpect.EOF)
        
    error_text = before(process)
    print(error_format.format(error_text))
    exitScript(process)


def exitScript(process=None):
    if process is not None:
        process.kill(0)
    quit()


def before(process):
    """Utility method to strip and decode a pexpect process' before output"""
    return process.before.decode("utf-8").strip()


def try_create_temp_dir(path):
    """Creates temporary directory, returning (path of temporary directory, whether the directory already existed)

    Defaults to 'temp'"""
    if path is None:
        path = DEFAULT_TEMP_DIR

    resolved = resolve_path(path)
    if try_make_dir(resolved):
        print("""Temporary dir "{}" created""".format(resolved))
        return resolved, False
    else:
        print("""Temporary dir "{}" already exists""".format(resolved))
        return resolved, True


def resolve_path(path):
    """Resolves an absolute/relative path to an absolute one (relative to current file's parent if applicable)"""
    if not os.path.isabs(path):
        return (Path(__file__).parent / path).resolve()
    else:
        return path


def try_make_dir(path):
    """Tries to make the directory at the path, and returns true if it succeeded and false if the file already existed
    (other IO errors are unhandled)"""
    try:
        os.mkdir(path)
        return True
    except FileExistsError:
        return False


def construct_non_none_tuple(a, b):
    """Returns a tuple of two non-none values, or None if either arguments are None"""
    if a is not None and b is not None:
        return a, b
    else:
        return None


# Run script
if __name__ == "__main__":
    # Argument definitions
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('source',        metavar='sourceRepo', help='the source github repository')
    parser.add_argument('dest',          metavar='destRepo',   help='the destination github repository')
    parser.add_argument('--sourceUser',  metavar='user',       help='authentication user for the source repo')
    parser.add_argument('--sourceToken', metavar='token',      help='authentication token/password for the source repo')
    parser.add_argument('--destUser',    metavar='user',       help='authentication user for the dest repo')
    parser.add_argument('--destToken',   metavar='token',      help='authentication token/password for the dest repo')
    parser.add_argument('--temp',        metavar='path',       help='temp directory for cloning the source repo')
    parser.add_argument('--remote',      metavar='name',       help='name of the destination remote to use')
    parser.add_argument('--timeout',     metavar='ms',         help='max amount of time to wait between command parses')

    # Parse arguments
    args = parser.parse_args()
    sourceAuth = construct_non_none_tuple(args.sourceUser, args.sourceToken)
    destAuth   = construct_non_none_tuple(args.destUser,   args.destToken)
    main(args.source, args.dest, source_auth=sourceAuth, dest_auth=destAuth,
        temp_dir=args.temp, remote=args.remote, timeout=args.timeout)
