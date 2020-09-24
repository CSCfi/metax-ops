# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import logging.config
import sys
import subprocess
import fileinput


def main():
    """
    copy requirements and find differences
    """
    try:
        req_new, req_org, req_changes = sys.argv[1:4]
    except:
        _logger.error('Give two files for comparison and one for writing changes')
        exit()

    with open(req_new, 'r') as f:
        f_new = set(f.readlines())
        f_new.discard('\n')
        f_new = set(map(lambda x: x.lower(), f_new))
    with open(req_org, 'r') as f:
        f_org = set(f.readlines())
        f_org.discard('\n')
        f_org = set(map(lambda x: x.lower(), f_org))

    changes = {}
    new = list(f_new - f_org)
    old = list(f_org - f_new)

    for line in new:
        line = line.replace('\n', '')
        try:
            line = line.split('==')
            changes[line[0].lower()] = {'new':line[1].lower(), 'old': None}

        except:
            _logger.error('%s' %line)
            continue

    for line in old:
        line = line.replace('\n', '')
        try:
            line = line.split('==')
            key_old = line[0].lower()
            value_old = line[1].split('#')[0].rstrip()

            if changes.get(key_old):
                changes[key_old]['old'] = value_old
            else:
                changes[key_old] = {'new': None, 'old': value_old}

        except:
            _logger.error('%s' %line)
            continue

    with open(req_changes, 'w') as f:
        json.dump(changes, f)

    print(f"""Requirements causing tests to fail are:
        {json.dumps(changes, sort_keys=True, indent=2)}
        Changes are saved to file {req_changes}.
        """)

if __name__ == '__main__':
    # setting up logger
    with open('logconf.json', 'r') as f:
        json_file = json.load(f)
    _logger = logging.getLogger('api_dependencies')
    logging.config.dictConfig(json_file)

    # calling main function
    main()