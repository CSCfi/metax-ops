import sys
from domain.organization_data import OrganizationData
from domain.reference_data import ReferenceData
from service.elasticsearch_service import ElasticSearchService
from service.finto_data_service import FintoDataService
from service.local_data_service import LocalDataService
from service.organization_service import OrganizationService
from service.infra_data_service import InfraDataService

def main():
    '''
    Runner file for indexing data to elasticsearch. Make sure requirementx.txt is installed via pip.
    '''
    NO = 'no'
    ALL = 'all'
    REMOVE_AND_RECREATE_INDEX = 'remove_and_recreate_index'
    TYPES_TO_REINDEX = 'types_to_reindex'

    instructions = """\nRun the program as metax-user with pyenv activated using 'python es_index_data.py remove_and_recreate_index=INDEX types_to_reindex=TYPE', where either or both of the arguments should be provided with one of the following values per argument:\n\nINDEX:\n{indices}\n\nTYPE:\n{types}"""
    instructions = instructions.format(indices=str([NO, ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME]), types=str([NO, ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, OrganizationData.DATA_TYPE_ORGANIZATION] + ReferenceData.FINTO_REFERENCE_DATA_TYPES + ReferenceData.LOCAL_REFERENCE_DATA_TYPES + [ReferenceData.DATA_TYPE_RESEARCH_INFRA]))

    run_args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])
    remove_and_recreate_index = None
    types_to_reindex = None

    if not REMOVE_AND_RECREATE_INDEX in run_args and not TYPES_TO_REINDEX in run_args:
        print(instructions)
        sys.exit(1)

    if REMOVE_AND_RECREATE_INDEX in run_args:
        remove_and_recreate_index = run_args[REMOVE_AND_RECREATE_INDEX]
        if remove_and_recreate_index not in [NO, ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME]:
            print(instructions)
            sys.exit(1)

    if TYPES_TO_REINDEX in run_args:
        types_to_reindex = run_args[TYPES_TO_REINDEX]
        if types_to_reindex not in ([NO, ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME] + ReferenceData.FINTO_REFERENCE_DATA_TYPES + ReferenceData.LOCAL_REFERENCE_DATA_TYPES + [ReferenceData.DATA_TYPE_RESEARCH_INFRA]):
            print(instructions)
            sys.exit(1)

    es = ElasticSearchService()

    if types_to_reindex in ([ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME] + ReferenceData.FINTO_REFERENCE_DATA_TYPES):
        finto_service = FintoDataService()

    if types_to_reindex in ([ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME] + ReferenceData.LOCAL_REFERENCE_DATA_TYPES):
        local_service = LocalDataService()

    if types_to_reindex in [ALL, ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME]:
        org_service = OrganizationService()

    if types_to_reindex in ([ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ReferenceData.DATA_TYPE_RESEARCH_INFRA]):
        infra_service = InfraDataService()

    if remove_and_recreate_index in [ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME]:
        es.delete_index(ElasticSearchService.REFERENCE_DATA_INDEX_NAME)

    if remove_and_recreate_index in [ALL, ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME]:
        es.delete_index(ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME)

    # Create reference data index and type mappings
    if not es.index_exists(ElasticSearchService.REFERENCE_DATA_INDEX_NAME):
        es.create_index(ElasticSearchService.REFERENCE_DATA_INDEX_NAME,
            ElasticSearchService.REFERENCE_DATA_INDEX_FILENAME)

        for doc_type in ReferenceData.FINTO_REFERENCE_DATA_TYPES + ReferenceData.LOCAL_REFERENCE_DATA_TYPES + [ReferenceData.DATA_TYPE_RESEARCH_INFRA]:
            es.create_type_mapping(ElasticSearchService.REFERENCE_DATA_INDEX_NAME,
                doc_type,
                ElasticSearchService.REFERENCE_DATA_TYPE_MAPPING_FILENAME)

    # Create organization data index and type mapping
    if not es.index_exists(ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME):
        es.create_index(ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME,
            ElasticSearchService.ORGANIZATION_DATA_INDEX_FILENAME)

        es.create_type_mapping(ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME,
            OrganizationData.DATA_TYPE_ORGANIZATION,
            ElasticSearchService.ORGANIZATION_DATA_TYPE_MAPPING_FILENAME)

    # Reindexing for Finto data
    if types_to_reindex in [ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME]:
        for data_type in ReferenceData.FINTO_REFERENCE_DATA_TYPES:
            es.delete_and_update_indexable_data(ElasticSearchService.REFERENCE_DATA_INDEX_NAME, data_type, finto_service.get_data(data_type))
    elif types_to_reindex in ReferenceData.FINTO_REFERENCE_DATA_TYPES:
        es.delete_and_update_indexable_data(ElasticSearchService.REFERENCE_DATA_INDEX_NAME, types_to_reindex, finto_service.get_data(types_to_reindex))

    # Reindexing local data
    if types_to_reindex in [ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME]:
        for data_type in ReferenceData.LOCAL_REFERENCE_DATA_TYPES:
            es.delete_and_update_indexable_data(ElasticSearchService.REFERENCE_DATA_INDEX_NAME, data_type, local_service.get_data(data_type))
    elif types_to_reindex in ReferenceData.LOCAL_REFERENCE_DATA_TYPES:
        es.delete_and_update_indexable_data(ElasticSearchService.REFERENCE_DATA_INDEX_NAME, types_to_reindex, local_service.get_data(types_to_reindex))

    # Reindexing organizations
    if types_to_reindex in [ALL, OrganizationData.DATA_TYPE_ORGANIZATION]:
        es.delete_and_update_indexable_data(ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME, OrganizationData.DATA_TYPE_ORGANIZATION, org_service.get_data())

    # Reindexing Infras
    if types_to_reindex in [ALL, ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ReferenceData.DATA_TYPE_RESEARCH_INFRA]:
        es.delete_and_update_indexable_data(ElasticSearchService.REFERENCE_DATA_INDEX_NAME, ReferenceData.DATA_TYPE_RESEARCH_INFRA, infra_service.get_data())
    print("Done")
    sys.exit(0)


if __name__ == '__main__':
    # calling main function
    main()
