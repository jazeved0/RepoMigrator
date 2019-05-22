import migrate
import argparse
import shutil

__author__ = "Joseph Azevedo"
__version__ = "1.0"

DESCRIPTION = "Migrates multiple repositories at once"
HTTPS_START = "https://"
REPO_FORMAT = "{}/{}/{}.git"


def main(source_site, dest_site, repos, dest_user=None, dest_token=None, source_user=None, source_token=None,
         temp_dir=None, remote=None, timeout=None):
    if not source_site.startswith(HTTPS_START):
        source_site = HTTPS_START + source_site
    if not dest_site.startswith(HTTPS_START):
        dest_site = HTTPS_START + dest_site

    source_auth = migrate.construct_non_none_tuple(source_user, source_token)
    dest_auth   = migrate.construct_non_none_tuple(dest_user,   dest_token)
    temp_path, temp_existed_before = migrate.try_create_temp_dir(temp_dir)

    for repo in repos:
        user = source_user
        dest_user = dest_user
        repo_name = repo

        if "/" in repo:
            split_str = repo.split("/")
            user = split_str[0]
            repo_name = split_str[1]

        if user is None:
            print("A user on the source site must be specified")
            exit()
        if dest_user is None:
            print("A user on the destination site must be specified")
            exit()

        source_repo = REPO_FORMAT.format(source_site, user,      repo_name)
        dest_repo   = REPO_FORMAT.format(dest_site,   dest_user, repo_name)
        migrate.migrate(source_repo, dest_repo, source_auth=source_auth, dest_auth=dest_auth,
                        temp_dir=temp_dir, remote=remote, timeout=timeout)

    try:
        if not temp_existed_before:
            shutil.rmtree(temp_path)
    except OSError as e:
        print ("An error occurred in cleanup. Exiting")
        quit()


# Run script
if __name__ == "__main__":
    # Argument definitions
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('source',            metavar='src_site',  help='the source github site')
    parser.add_argument('dest',              metavar='dest_site', help='the destination github site')
    parser.add_argument('repos', nargs='+',  metavar='repo',  help='each source repo to use; either user/repo or repo')
    parser.add_argument('--sourceUser',      metavar='user',  help='authentication user for the source repo(s)')
    parser.add_argument('--sourceToken',   metavar='token', help='authentication token/password for the source repo(s)')
    parser.add_argument('--destUser',        metavar='user',  help='authentication user for the dest repo(s)',
                        required=True)
    parser.add_argument('--destToken',       metavar='token', help='authentication token/password for the dest repo(s)')
    parser.add_argument('--temp',            metavar='path',  help='temp directory for cloning the source repo(s)')
    parser.add_argument('--remote',          metavar='name',  help='name of the destination remote to use')
    parser.add_argument('--timeout',         metavar='ms',    help='max amount of time to wait between command parses')

    # Parse arguments
    args = parser.parse_args()
    main(args.source, args.dest, args.repos, args.destUser, args.destToken, args.sourceUser, args.sourceToken,
         temp_dir=args.temp, remote=args.remote, timeout=args.timeout)
