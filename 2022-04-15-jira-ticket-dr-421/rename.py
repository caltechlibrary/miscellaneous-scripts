#!/usr/bin/env python3
# =============================================================================
# @file    rename.py
# @brief   Rename files per request
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/miscellaneous-scripts
#
# Script for https://caltechlibrary.atlassian.net/jira/servicedesk/projects/DR/queues/custom/23/DR-421
# =============================================================================

import click
import glob
from   rich.console import Console
from   rich.style import Style
from   rich.panel import Panel
import os
from   os import path
import re
import shutil

console = Console()
prt     = console.print

# Helper functions.
# .............................................................................

def inform(msg): prt('[white]' + msg + '[/]')
def warn(msg):   prt('[yellow]' + msg + '[/]')
def alert(msg):  prt('[red]' + msg + '[/]')
def fail(msg):   prt(Panel(msg, style = Style.parse('red'), width = 60)); exit(1)

# Main code.
# .............................................................................

@click.command()
@click.option('-n', '--dry-run', is_flag = True, default = False)

def rename(dry_run):
    # Do some sanity checking first.
    if not path.exists('documents'):
        fail('This script assumes files are in a subdirectory named "documents"')

    # Define a helper function that uses the command-line argument value.
    def move(src, dest):
        if not dry_run:
            shutil.move(src, dest)

    # All paths after this point in the script will be relative to the documents dir
    os.chdir('documents')

    # Create directories where we move some of the files.
    for name in ['unrecognized', 'inconsistent', 'counter', 'done']:
        if not path.exists(name) and not path.isdir(name):
            os.mkdir(name)

    # Define a matcher for dates in the file names.
    date_regex = re.compile(r'(?P<year>\d{4})'
                            r'([_-]'
                                r'(?P<month>\d{1,2})'
                                r'([_-](?P<day>\d{1,2}))?'
                            r')?'
                            r'(?P<trailing_char>[^0-9])(?:[^0-9])')

    # Iterate over all files that start with a 4-digit year and do our thing.
    matching_files = glob.glob('[0-9][0-9][0-9][0-9]*')
    inform(f'Found {len(matching_files)} files beginning with dates.')
    done = 0
    skipped = 0
    for file in matching_files:
        parts = file.split('.')

        # Filter out files we can't recognize or deliberately ignore.
        if len(parts) > 2:
            alert(f'Unrecognized file name structure: "{file}"')
            move(file, path.join('unrecognized', file))
            skipped += 1
            continue
        base, ext = parts[0], parts[1]
        if 'counter' in base.lower():
            warn(f'Counter file: "{file}"')
            move(file, path.join('counter', file))
            skipped += 1
            continue
        matched = date_regex.match(base)
        if not matched:
            alert(f'Inconsistent file name: "{file}"')
            move(file, path.join('inconsistent', file))
            skipped += 1
            continue

        year  = matched.group('year')
        month = matched.group('month')
        day   = matched.group('day')
        char  = matched.group('trailing_char')

        if char not in ['-', '_']:
            alert(f'Inconsistent file name: "{file}"')
            move(file, path.join('inconsistent', file))
            skipped += 1
            continue

        date = year
        if month:
            date += ('_' + month.zfill(2))
        if day:
            date += ('_' + day.zfill(2))

        rest_start = len(matched.group(0)) - 1
        rest = base[rest_start:].split('_')
        if len(rest) < 2:
            alert(f'Inconsistent file name: "{file}"')
            move(file, path.join('inconsistent', file))
            skipped += 1
            continue

        # We're left with files we can process. Our goal is to convert
        #       YYYY[-MM]_Doctype_Organization[_Notes]
        # to    Organization_YYYY-[MM]_Doctype[_Notes]
        doctype = rest[0]
        org     = rest[1]
        notes   = ('_' + '_'.join(rest[2:])) if rest[2:] else ''
        new_name = f'{org}_{date}_{doctype}{notes}.{ext}'
        inform(f'Renamed {file} → {new_name}')
        move(file, path.join('done', new_name))
        done += 1

    total = len(matching_files)
    msg = f'Done. {total} total files, {done} renamed, {skipped} files skipped.'
    prt(Panel(msg, style = Style.parse('green'), width = 60))


if __name__ == '__main__':
    rename()
