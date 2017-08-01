from domain.indexable_data import IndexableData

class OrganizationData(IndexableData):
    '''
    Model class for organization data that can be indexed into Metax Elasticsearch
    '''

    DATA_TYPE_ORGANIZATION = 'organization'

    def __init__(
        self,
        org_id,
        label,
        uri='',
        parent_id='',
        parent_label=''):

        super(OrganizationData, self).__init__(org_id, OrganizationData.DATA_TYPE_ORGANIZATION)

        self.label = label # { 'fi': 'value1', 'en': 'value2',..., 'default': 'default_value' }
        self.uri = uri
        self.parent_id = parent_id
        self.parent_label = parent_label

    def __str__(self):
        return (
            "{" +
                "\"id\":\"" + self.doc_id + "\","
                "\"uri\":\"" + self.uri + "\","
                "\"label\":\"" + str(self.label) + "\","
                "\"parent_id\":\"" + self.parent_id + "\","
                "\"parent_label\":\"" + self.parent_label + "\""
            "}")
