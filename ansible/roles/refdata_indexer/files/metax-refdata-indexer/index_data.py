# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import logging.config
import sys

from domain.indexable_data import IndexableData
from domain.reference_data import ReferenceData as refdata
from domain.organization_data import OrganizationData as orgdata
from service.elasticsearch_service import ElasticSearchService


es = ElasticSearchService()
refdata_dir = ''

def _delete_and_update_indexable_data(ref_type, data_type, index=es.REF_DATA_INDEX_NAME):
    _logger.info("Reading data for {} data type {}".format(ref_type, data_type))
    try:
        with open('{}/{}_{}.es_ref'.format(refdata_dir, ref_type, data_type), 'r') as f:
            es_data_models = f.read()

            es_data_models_list = []
            for data in es_data_models.split('\n'):
                if len(data) > 0:
                    data_dict = json.loads(data)
                    if ref_type == 'org':
                        data = orgdata(
                            data_dict.get('code'),
                            data_dict.get('label'),
                            data_dict.get('parent_id', None),
                            data_dict.get('same_as', []),
                            data_dict.get('org_csc', None),
                            data_dict.get('scheme', None)
                        )
                    else:
                        data = refdata(
                            data_dict.get('code'),
                            data_dict.get('type'),
                            data_dict.get('label'),
                            data_dict.get('uri'),
                            data_dict.get('parent_ids', []),
                            data_dict.get('child_ids', []),
                            data_dict.get('same_as', []),
                            data_dict.get('wkt', None),
                            data_dict.get('input_file_format', None),
                            data_dict.get('output_format_version', None),
                            data_dict.get('scheme', None),
                            data_dict.get('internal_code', None)
                        )
                    es_data_models_list.append(data)
            _logger.info('ok')
            es.delete_and_update_indexable_data(index, data_type, es_data_models_list)
    except FileNotFoundError as e:
        _logger.error("{}\nNo data models to reindex for {} data type {}".format(e, ref_type, data_type))
        pass

def parse_files(files):
    files = files.split('\n')
    parsed_files = {
        'remove_and_recreate_index': [],
        'types_to_reindex': []
    }

    for file in files:
        file = file.strip()
        if file:
            ref_type, data_type = file.split('_', 1)
            if ref_type == 'org':
                parsed_files['remove_and_recreate_index'].append(es.ORG_DATA_INDEX_NAME)
            else:
                parsed_files['remove_and_recreate_index'].append(es.REF_DATA_INDEX_NAME)
            parsed_files['types_to_reindex'].append(data_type.split('.es_ref')[0])
    return parsed_files

def main():
    '''
    Runner file for indexing data to elasticsearch. Make sure requirementx.txt is installed via pip.
    '''

    global refdata_dir

    NO = 'no'
    ALL = 'all'
    REMOVE_AND_RECREATE_INDEX = 'remove_and_recreate_index'
    TYPES_TO_REINDEX = 'types_to_reindex'

    INDICES = [NO, ALL, es.REF_DATA_INDEX_NAME, es.ORG_DATA_INDEX_NAME]
    TYPES = [NO, ALL, es.REF_DATA_INDEX_NAME, IndexableData.DATA_TYPE_ORGANIZATION] + \
        refdata.FINTO_REF_DATA_TYPES + refdata.LOCAL_REF_DATA_TYPES + \
        [refdata.DATA_TYPE_RESEARCH_INFRA, refdata.DATA_TYPE_MIME_TYPE]

    instructions = """
            Run the program as metax-user with pyenv activated using
            'python index_data.py refdata_path=DIRECTORY remove_and_recreate_index=INDEX types_to_reindex=TYPE',
            where either or both of the arguments should be provided with one of the following values per argument:

            DIRECTORY:
            Path to git repository or directory where parsed reference data resides

            INDEX:
            {indices}

            TYPE:
            {types}
            """
    instructions = instructions.format(indices=str(INDICES), types=str(TYPES))

    run_args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])
    remove_and_recreate_index = None
    types_to_reindex = None

    run_args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])

    if 'refdata_path' not in run_args:
        _logger.error(instructions)
        sys.exit(1)
    else:
        refdata_dir = run_args['refdata_path']

    if run_args.get('files_changed'):
        run_args = parse_files(run_args['files_changed'])

    if REMOVE_AND_RECREATE_INDEX not in run_args and TYPES_TO_REINDEX not in run_args:
        _logger.error(instructions)
        sys.exit(1)

    if REMOVE_AND_RECREATE_INDEX in run_args:
        remove_and_recreate_index = run_args[REMOVE_AND_RECREATE_INDEX]
        if remove_and_recreate_index not in INDICES and not any(d in INDICES for d in remove_and_recreate_index):
            _logger.error(instructions)
            sys.exit(1)

    if TYPES_TO_REINDEX in run_args:
        types_to_reindex = run_args[TYPES_TO_REINDEX]
        if types_to_reindex not in TYPES and not any(d in TYPES for d in types_to_reindex):
            _logger.error(instructions)
            sys.exit(1)

    if remove_and_recreate_index in [ALL, es.REF_DATA_INDEX_NAME] or \
            any(d in [ALL, es.REF_DATA_INDEX_NAME] for d in remove_and_recreate_index):
        es.delete_index(es.REF_DATA_INDEX_NAME)

    if remove_and_recreate_index in [ALL, es.ORG_DATA_INDEX_NAME] or \
            any(d in [ALL, es.ORG_DATA_INDEX_NAME] for d in remove_and_recreate_index):
        es.delete_index(es.ORG_DATA_INDEX_NAME)

    # import ipdb; ipdb.launch_ipdb_on_exception() #ipdb.set_trace()

    # Create reference data index with mappings
    if not es.index_exists(es.REF_DATA_INDEX_NAME):
        print('no existing REF_DATA index, creating.....')
        es.create_index(es.REF_DATA_INDEX_NAME, es.REF_DATA_INDEX_FILENAME)

    # Create organization data index with mappings
    if not es.index_exists(es.ORG_DATA_INDEX_NAME):
        print('no existing ORG_DATA index, creating.....')
        es.create_index(es.ORG_DATA_INDEX_NAME, es.ORG_DATA_INDEX_FILENAME)

    # Reindexing for Finto data
    if types_to_reindex in [ALL, es.REF_DATA_INDEX_NAME]:
        for data_type in refdata.FINTO_REF_DATA_TYPES:
            _delete_and_update_indexable_data('finto', data_type)
    elif any(d in refdata.FINTO_REF_DATA_TYPES for d in types_to_reindex):
        for data_type in types_to_reindex:
            if data_type in refdata.FINTO_REF_DATA_TYPES:
                _delete_and_update_indexable_data('finto', data_type)
    elif types_to_reindex in refdata.FINTO_REF_DATA_TYPES:
        _delete_and_update_indexable_data('finto', types_to_reindex)

    # Reindexing local data
    if types_to_reindex in [ALL, es.REF_DATA_INDEX_NAME]:
        for data_type in refdata.LOCAL_REF_DATA_TYPES:
            _delete_and_update_indexable_data('local', data_type)
    elif any(d in refdata.LOCAL_REF_DATA_TYPES for d in types_to_reindex):
        for data_type in types_to_reindex:
            if data_type in refdata.LOCAL_REF_DATA_TYPES:
                _delete_and_update_indexable_data('local', data_type)
    elif types_to_reindex in refdata.LOCAL_REF_DATA_TYPES:
        _delete_and_update_indexable_data('local', types_to_reindex)

    # Reindexing organizations
    if types_to_reindex in [ALL, IndexableData.DATA_TYPE_ORGANIZATION] or \
            IndexableData.DATA_TYPE_ORGANIZATION in types_to_reindex:
        _delete_and_update_indexable_data('org', IndexableData.DATA_TYPE_ORGANIZATION,
                index=es.ORG_DATA_INDEX_NAME)

    # Reindexing infras
    if types_to_reindex in [ALL, es.REF_DATA_INDEX_NAME, refdata.DATA_TYPE_RESEARCH_INFRA] or \
            refdata.DATA_TYPE_RESEARCH_INFRA in types_to_reindex:
        _delete_and_update_indexable_data('infra', refdata.DATA_TYPE_RESEARCH_INFRA)

    # Reindexing mime types
    if types_to_reindex in [ALL, es.REF_DATA_INDEX_NAME, refdata.DATA_TYPE_MIME_TYPE] or \
            refdata.DATA_TYPE_MIME_TYPE in types_to_reindex:
        _delete_and_update_indexable_data('mime', refdata.DATA_TYPE_MIME_TYPE)

    _logger.info("Done")
    sys.exit(0)


if __name__ == '__main__':
    # setting up logger
    with open('logconf.json', 'r') as f:
        json_file = json.load(f)
    _logger = logging.getLogger('refdata_indexer')
    logging.config.dictConfig(json_file)

    # calling main function
    main()
