from domain.indexable_data import IndexableData
from service.elasticsearch_service import ElasticSearchService
from service.service_utils import set_default_label

class OrganizationData(IndexableData):
    '''
    Model class for organization data that can be indexed into Metax Elasticsearch
    '''

    DATA_TYPE_ORGANIZATION = 'organization'
    ORGANIZATION_PURL_BASE_URL = 'http://purl.org/att/es/' + ElasticSearchService.ORGANIZATION_DATA_INDEX_NAME + "/" + DATA_TYPE_ORGANIZATION

    def __init__(
        self,
        org_id,
        label,
        parent_id='',
        parent_label='',
        same_as=[],
        org_csc=''):

        super(OrganizationData, self).__init__(org_id, OrganizationData.DATA_TYPE_ORGANIZATION, label, OrganizationData.ORGANIZATION_PURL_BASE_URL + '/' + org_id, same_as)
        self.parent_id = ''
        if parent_id:
            self.parent_id = self._create_es_document_id(parent_id)
        self.parent_label = parent_label
        set_default_label(self.parent_label)
        self.org_csc = org_csc

    def __str__(self):
        return (
            "{" +
                "\"id\":\"" + self.get_es_document_id() + "\","
                "\"code\":\"" + self.code + "\","
                "\"type\":\"" + self.DATA_TYPE_ORGANIZATION + "\","
                "\"uri\":\"" + self.uri + "\","
                "\"label\":\"" + str(self.label) + "\","
                "\"parent_id\":\"" + self.parent_id + "\","
                "\"parent_label\":\"" + str(self.parent_label) + "\","
                "\"same_as\":\"" + str(self.same_as) + "\","
                "\"org_csc\":\"" + self.org_csc + "\""
            "}")
