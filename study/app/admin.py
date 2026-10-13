"""Host-only account administration and consistent SQLite backups."""
import argparse
from contextlib import closing
import getpass
from pathlib import Path
import sqlite3
import sys
from app.accounts import create_user, reset_password
from app.database import database


def main():
    """Prompt for secrets interactively instead of accepting password arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('create-user', 'reset-password'):
        commands.add_parser(name).add_argument('username')
    commands.add_parser('backup-db').add_argument('destination')
    args = parser.parse_args()
    try:
        if args.command == 'backup-db':
            destination = Path(args.destination)
            if destination.exists():
                raise ValueError('Backup destination already exists.')
            # Reserve a private file; sqlite's backup API includes committed WAL data.
            destination.touch(mode=0o600, exist_ok=False)
            try:
                with database() as source, closing(sqlite3.connect(destination)) as target:
                    source.backup(target)
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            print(f'Backup written to {destination}')
            return
        if not sys.stdin.isatty():
            raise ValueError('Use an interactive terminal (docker compose exec without -T) for passwords.')
        password = getpass.getpass('Password: ')
        if password != getpass.getpass('Confirm password: '):
            raise ValueError('Passwords do not match.')
        (create_user if args.command == 'create-user' else reset_password)(args.username, password)
        print('Account created.' if args.command == 'create-user' else 'Password reset; all sessions revoked.')
    except (ValueError, sqlite3.Error, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
