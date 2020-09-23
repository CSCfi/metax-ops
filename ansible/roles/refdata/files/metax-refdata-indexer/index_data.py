# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import logging.config
import os
import sys

import domain.datatypes as types
from service.elasticsearch_service import ElasticSearchService


es = ElasticSearchService()

def _delete_and_update_indexable_data(refdata_path, data_type):
    """
    Wrapper to call elasticsearch service with correct parameters.
    Determines filename and index for given data_type and calls the service.
    """
    if data_type in types.FINTO_TYPES:
        ref_type = 'finto'
    elif data_type in types.LOCAL_TYPES:
        ref_type = 'local'
    elif data_type in types.MIME_TYPE:
        ref_type = 'mime'
    elif data_type in types.ORG_TYPE:
        ref_type = 'org'

    if data_type in types.REFDATA_TYPES:
        index = 'reference_data'
    elif data_type in types.ORGDATA_TYPES:
        index = 'organization_data'

    _logger.info("Reading data {}".format(data_type))

    try:
        with open('{}/{}_{}.es_ref'.format(refdata_path, ref_type, data_type), 'r') as f:
            indexable_data_list = f.readlines()

        _logger.info('Data for {} loaded successfully'.format(data_type))
        es.delete_and_update_indexable_data(index, data_type, indexable_data_list)

    except FileNotFoundError as e:
        _logger.error(e)
        _logger.info("No data to reindex for {} data type {}".format(ref_type, data_type))
        pass

def main():
    help_text = """
    Runner file for indexing data to elasticsearch. Make sure requirements.txt is installed via pip.

    params:
        refdata_path (required): path to reference data repository which is checked out to release tag.

        indices_to_recreate (required):
            Comma separated list of indices that are recreated before indexing. Can also take
            value 'all' when all the indexes are recreated and 'no' when no indexes are recreated.

        types_to_reindex (required):
            Comma separated list of all types that are indexed.
            Ingests also values 'all', 'no' or the name of an index. If index name is given,
            all the types in that index are reindexed.
    """

    ALL = 'all'

    run_args = sys.argv[1:]

    if len(run_args) < 3:
        print(help_text)
        exit(1)

    refdata_path = run_args[0]
    indices_to_recreate = run_args[1].split(',')
    types_to_reindex = run_args[2].split(',')

    if any(i in [ALL, es.REF_DATA_INDEX_NAME] for i in indices_to_recreate):
        es.delete_index(es.REF_DATA_INDEX_NAME)

    if any(i in [ALL, es.ORG_DATA_INDEX_NAME] for i in indices_to_recreate):
        es.delete_index(es.ORG_DATA_INDEX_NAME)

    # Create reference data index with mappings
    if not es.index_exists(es.REF_DATA_INDEX_NAME):
        _logger.info('no existing REF_DATA index, creating.....')
        es.create_index(es.REF_DATA_INDEX_NAME, es.REF_DATA_INDEX_FILENAME)

    # Create organization data index with mappings
    if not es.index_exists(es.ORG_DATA_INDEX_NAME):
        _logger.info('no existing ORG_DATA index, creating.....')
        es.create_index(es.ORG_DATA_INDEX_NAME, es.ORG_DATA_INDEX_FILENAME)

    reindexed_types = set()

    if 'all' in types_to_reindex:
        reindexed_types.update(types.ALL_TYPES)
        types_to_reindex.remove('all')

    if es.REF_DATA_INDEX_NAME in types_to_reindex:
        reindexed_types.update(types.REFDATA_TYPES)
        types_to_reindex.remove(es.REF_DATA_INDEX_NAME)

    if es.ORG_DATA_INDEX_NAME in types_to_reindex:
        reindexed_types.update(types.ORGDATA_TYPES)
        types_to_reindex.remove(es.ORG_DATA_INDEX_NAME)

    reindexed_types.update(types_to_reindex)

    for type in reindexed_types:
        _delete_and_update_indexable_data(refdata_path, type)

    _logger.info("Done")


if __name__ == '__main__':
    # setting up logger
    with open(os.path.abspath('logconf.json')) as f:
        json_file = json.load(f)
    _logger = logging.getLogger('refdata_indexer.index_data')
    logging.config.dictConfig(json_file)

    main()

    sys.exit(0)
