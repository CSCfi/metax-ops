# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import sys
import logging
import logging.config

from domain.indexable_data import IndexableData
from domain.reference_data import ReferenceData
from service.finto_data_service import FintoDataService
from service.infra_data_service import InfraDataService
from service.local_data_service import LocalDataService
from service.mime_data_service import MimeDataService
from service.organization_service import OrganizationService


def write_to_file(repo, ref_type, data):
    '''
    File for writing data to git repository.
    '''

    with open('{}/{}.es_ref'.format(repo, ref_type), 'w') as gitfile:
        for ref in data:
            gitfile.write(str(ref) + '\n')
        ('Written {} to {}/{}.es_ref'.format(ref_type, repo, ref_type))
        _logger.info('Written {} to {}/{}.es_ref'.format(ref_type, repo, ref_type))

def main():
    # import ipdb; ipdb.launch_ipdb_on_exception() #ipdb.set_trace()

    if not sys.argv[1]:
        _logger.error('Please provide path to reference data repository')
        sys.exit(1)
    repo = sys.argv[1]

    # TODO in services: sort outcomming data by label or other static data
    # otherwise random ordering shows changes in data in git

    finto_service = FintoDataService()
    local_service = LocalDataService()
    org_service = OrganizationService()
    infra_service = InfraDataService()
    mime_service = MimeDataService()

    # TODO:??? loop
    # servises = {
    #     finto: {service: FintoDataService(), datatype: ReferenceData.FINTO_REFERENCE_DATA_TYPES},
    #     local: {service: LocalDataService(), datatype: ReferenceData.LOCAL_REFERENCE_DATA_TYPES},
    #     org: {service: OrganizationService(), datatype: IndexableData.DATA_TYPE_ORGANIZATION},
    #     infra: {service: InfraDataService(), datatype: ReferenceData.DATA_TYPE_RESEARCH_INFRA},
    #     mime: {service: MimeDataService(), datatype: ReferenceData.DATA_TYPE_MIME_TYPE}}
    # for service in services.keys():

    # get for Finto data
    for data_type in ReferenceData.FINTO_REF_DATA_TYPES:
        finto_data_models = finto_service.get_data(data_type)
        if len(finto_data_models) == 0:
            _logger.info("No data models to get for finto data type {0}".format(data_type))
            continue
        else:
            _logger.info('Getting FINTO data: finto_' + data_type)
            write_to_file(repo, 'finto_' + data_type, finto_data_models)

    # get local data
    for data_type in ReferenceData.LOCAL_REF_DATA_TYPES:
        local_data_models = local_service.get_data(data_type)
        if len(local_data_models) == 0:
            _logger.info("No data models to get for local data type {0}".format(data_type))
        else:
            _logger.info('Getting LOCAL data: local_' + data_type)
            write_to_file(repo, 'local_' + data_type, local_data_models)

    # get organizations
    data_type = IndexableData.DATA_TYPE_ORGANIZATION
    org_data_models = org_service.get_data()
    if len(org_data_models) == 0:
        _logger.info("No data models to get for organizational data")
    else:
        _logger.info('Getting ORG data')
        write_to_file(repo, 'org_' + data_type, org_data_models)

    # get infras
    data_type = ReferenceData.DATA_TYPE_RESEARCH_INFRA
    infra_data_models = infra_service.get_data()
    if len(infra_data_models) == 0:
        _logger.info("No data models to reindex for infra data type")
    else:
        _logger.info('Getting INFRA data')
        write_to_file(repo, 'infra_' + data_type, infra_data_models)

    # get mime types
    data_type = ReferenceData.DATA_TYPE_MIME_TYPE
    mime_data_models = mime_service.get_data()
    if len(mime_data_models) == 0:
        _logger.info("no data models to reindex for mime type data type")
    else:
        _logger.info('Getting MIME data')
        write_to_file(repo, 'mime_' + data_type, mime_data_models)


if __name__ == '__main__':
    # setting up logger
    with open('logconf.json', 'r') as f:
        json_file = json.load(f)
    _logger = logging.getLogger('refdata_writer')
    logging.config.dictConfig(json_file)

    # calling main function
    main()
