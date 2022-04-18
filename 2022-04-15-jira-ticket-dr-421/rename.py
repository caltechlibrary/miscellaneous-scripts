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

import glob
from   rich.console import Console
from   rich.style import Style
from   rich.panel import Panel
import shutil
import os
from   os import path

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

# Do some sanity checking first.

if not path.exists('documents'):
    fail('This script assumes files are in a subdirectory named "documents"')

# All paths after this point in the script will be relative to the documents dir

os.chdir('documents')

# Create directories where we move some of the files.

for name in ['unrecognized', 'inconsistent', 'counter', 'done']:
    if not path.exists(name) and not path.isdir(name):
        os.mkdir(name)

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
        shutil.move(file, path.join('unrecognized', file))
        skipped += 1
        continue
    base, ext = parts[0], parts[1]
    if 'COUNTER' in base:
        warn(f'Counter file: "{file}"')
        shutil.move(file, path.join('counter', file))
        skipped += 1
        continue
    parts = base.split('_')
    if 2 >= len(parts):
        alert(f'Inconsistent file name: "{file}"')
        shutil.move(file, path.join('inconsistent', file))
        skipped += 1
        continue

    # We're left with files we can process. Our goal is to convert
    #       YYYY[-MM]_Doctype_Organization[_Notes]
    # to    Organization_YYYY-[MM]_Doctype[_Notes]
    date    = parts[0]
    doctype = parts[1]
    org     = parts[2]
    notes   = "_".join(parts[3:]) if parts[3:] else ''
    new_name = f'{org}_{date}_{doctype}{notes}.{ext}'
    inform(f'Renamed {file} → {new_name}')
    shutil.move(file, path.join('done', new_name))
    done += 1

total = len(matching_files)
msg = f'Done. {total} total files, {done} renamed, {skipped} files skipped.'
prt(Panel(msg, style = Style.parse('green'), width = 60))
