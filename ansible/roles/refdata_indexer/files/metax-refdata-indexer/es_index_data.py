# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import logging.config
import sys

from domain.indexable_data import IndexableData as IdxData
from domain.reference_data import ReferenceData as RefData
from service.elasticsearch_service import ElasticSearchService as ESS
from service.finto_data_service import FintoDataService
# from service.infra_data_service import InfraDataService
from service.local_data_service import LocalDataService
from service.mime_data_service import MimeDataService
from service.organization_service import OrganizationService


def main():
    '''
    Runner file for indexing data to elasticsearch. Make sure requirementx.txt is installed via pip.
    '''
    NO = 'no'
    ALL = 'all'
    REMOVE_AND_RECREATE_INDEX = 'remove_and_recreate_index'
    TYPES_TO_REINDEX = 'types_to_reindex'

    instructions = """
        \nRun the program as metax-user with pyenv activated using
        'python es_index_data.py remove_and_recreate_index=INDEX types_to_reindex=TYPE',
        where either or both of the arguments should be provided with one of the following values
        per argument:\n\nINDEX:\n{indices}\n\nTYPE:\n{types}
    """
    instructions = instructions.format(
        indices=str([NO, ALL, ESS.REF_DATA_INDEX_NAME, ESS.ORG_DATA_INDEX_NAME]),
        types=str(
            [NO, ALL, ESS.REF_DATA_INDEX_NAME, IdxData.DATA_TYPE_ORGANIZATION] +
            RefData.FINTO_REF_DATA_TYPES + RefData.LOCAL_REF_DATA_TYPES +
            [RefData.DATA_TYPE_RESEARCH_INFRA, RefData.DATA_TYPE_MIME_TYPE]
        )
    )

    run_args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])
    remove_and_recreate_index = None
    types_to_reindex = None

    if REMOVE_AND_RECREATE_INDEX not in run_args and TYPES_TO_REINDEX not in run_args:
        print(instructions)
        sys.exit(1)

    if REMOVE_AND_RECREATE_INDEX in run_args:
        remove_and_recreate_index = run_args[REMOVE_AND_RECREATE_INDEX]
        if remove_and_recreate_index not in [NO, ALL, ESS.REF_DATA_INDEX_NAME, ESS.ORG_DATA_INDEX_NAME]:
            print(instructions)
            sys.exit(1)

    if TYPES_TO_REINDEX in run_args:
        types_to_reindex = run_args[TYPES_TO_REINDEX]
        if types_to_reindex not in (
                [NO, ALL, ESS.REF_DATA_INDEX_NAME, IdxData.DATA_TYPE_ORGANIZATION] +
                RefData.FINTO_REF_DATA_TYPES + RefData.LOCAL_REF_DATA_TYPES +
                [RefData.DATA_TYPE_RESEARCH_INFRA, RefData.DATA_TYPE_MIME_TYPE]):

            print(instructions)
            sys.exit(1)

    es = ESS()

    if types_to_reindex in ([ALL, ESS.REF_DATA_INDEX_NAME] + RefData.FINTO_REF_DATA_TYPES):
        finto_service = FintoDataService()

    if types_to_reindex in ([ALL, ESS.REF_DATA_INDEX_NAME] + RefData.LOCAL_REF_DATA_TYPES):
        local_service = LocalDataService()

    if types_to_reindex in [ALL, IdxData.DATA_TYPE_ORGANIZATION]:
        org_service = OrganizationService()

    # if types_to_reindex in ([ALL, ESS.REF_DATA_INDEX_NAME, RefData.DATA_TYPE_RESEARCH_INFRA]):
    #     infra_service = InfraDataService()

    if types_to_reindex in ([ALL, ESS.REF_DATA_INDEX_NAME, RefData.DATA_TYPE_MIME_TYPE]):
        mime_service = MimeDataService()

    if remove_and_recreate_index in [ALL, ESS.REF_DATA_INDEX_NAME]:
        es.delete_index(ESS.REF_DATA_INDEX_NAME)

    if remove_and_recreate_index in [ALL, ESS.ORG_DATA_INDEX_NAME]:
        es.delete_index(ESS.ORG_DATA_INDEX_NAME)

    # Create reference data index with mappings
    if not es.index_exists(ESS.REF_DATA_INDEX_NAME):
        es.create_index(ESS.REF_DATA_INDEX_NAME,
            ESS.REF_DATA_INDEX_FILENAME)

    # Create organization data index with mappings
    if not es.index_exists(ESS.ORG_DATA_INDEX_NAME):
        es.create_index(ESS.ORG_DATA_INDEX_NAME,
            ESS.ORG_DATA_INDEX_FILENAME)

    # Reindexing for Finto data
    if types_to_reindex in [ALL, ESS.REF_DATA_INDEX_NAME]:
        for data_type in RefData.FINTO_REF_DATA_TYPES:
            finto_es_data_models = finto_service.get_data(data_type)
            if len(finto_es_data_models) == 0:
                _logger.info("No data models to reindex for finto data type {0}".format(data_type))
                continue

            es.delete_and_update_indexable_data(ESS.REF_DATA_INDEX_NAME, data_type, finto_es_data_models)
    elif types_to_reindex in RefData.FINTO_REF_DATA_TYPES:
        finto_es_data_models = finto_service.get_data(types_to_reindex)
        if len(finto_es_data_models) > 0:
            es.delete_and_update_indexable_data(ESS.REF_DATA_INDEX_NAME, types_to_reindex, finto_es_data_models)
        else:
            _logger.info("No data models to reindex for finto data type {0}".format(types_to_reindex))

    # Reindexing local data
    if types_to_reindex in [ALL, ESS.REF_DATA_INDEX_NAME]:
        for data_type in RefData.LOCAL_REF_DATA_TYPES:
            es.delete_and_update_indexable_data(
                ESS.REF_DATA_INDEX_NAME,
                data_type,
                local_service.get_data(data_type)
            )
    elif types_to_reindex in RefData.LOCAL_REF_DATA_TYPES:
        es.delete_and_update_indexable_data(
            ESS.REF_DATA_INDEX_NAME,
            types_to_reindex,
            local_service.get_data(types_to_reindex)
        )

    # Reindexing organizations
    if types_to_reindex in [ALL, IdxData.DATA_TYPE_ORGANIZATION]:
        es.delete_and_update_indexable_data(
            ESS.ORG_DATA_INDEX_NAME,
            IdxData.DATA_TYPE_ORGANIZATION,
            org_service.get_data()
        )

    # Reindexing mime types
    if types_to_reindex in [ALL, ESS.REF_DATA_INDEX_NAME, RefData.DATA_TYPE_MIME_TYPE]:
        mime_es_data_models = mime_service.get_data()
        if len(mime_es_data_models) > 0:
            es.delete_and_update_indexable_data(
                ESS.REF_DATA_INDEX_NAME,
                RefData.DATA_TYPE_MIME_TYPE,
                mime_es_data_models
            )
        else:
            _logger.info("no data models to reindex for mime type data type")

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
