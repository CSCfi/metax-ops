from domain.indexable_data import IndexableData

class ReferenceData(IndexableData):
    '''
    Model class for reference data that can be indexed into Metax Elasticsearch
    '''

    DATA_TYPE_FIELD_OF_SCIENCE = 'field_of_science'
    DATA_TYPE_LANGUAGE = 'language'
    DATA_TYPE_LOCATION = 'location'
    DATA_TYPE_KEYWORD = 'keyword'

    DATA_TYPE_RESEARCH_INFRA = 'research_infra'

    DATA_TYPE_ACCESS_TYPE = 'access_type'
    DATA_TYPE_CHECKSUM_ALGORITHM_TYPE = 'checksum_algorithm_type'
    DATA_TYPE_RESOURCE_TYPE = 'resource_type'
    DATA_TYPE_MIME_TYPE = 'mime_type'
    DATA_TYPE_IDENTIFIER_TYPE = 'identifier_type'
    DATA_TYPE_ACCESS_RESTRICTION_GROUNDS_TYPE = 'access_restriction_grounds_type'
    DATA_TYPE_CONTRIBUTOR_ROLE_TYPE = 'contributor_role_type'
    DATA_TYPE_FUNDER_TYPE = 'funder_type'
    DATA_TYPE_LICENSE_TYPE = 'license_type'

    FINTO_REFERENCE_DATA_TYPES = [
        DATA_TYPE_FIELD_OF_SCIENCE,
        DATA_TYPE_LANGUAGE,
        DATA_TYPE_LOCATION,
        DATA_TYPE_KEYWORD
    ]

    LOCAL_REFERENCE_DATA_TYPES = [
        DATA_TYPE_ACCESS_TYPE,
        DATA_TYPE_CHECKSUM_ALGORITHM_TYPE,
        DATA_TYPE_RESOURCE_TYPE,
        DATA_TYPE_MIME_TYPE,
        DATA_TYPE_IDENTIFIER_TYPE,
        DATA_TYPE_ACCESS_RESTRICTION_GROUNDS_TYPE,
        DATA_TYPE_CONTRIBUTOR_ROLE_TYPE,
        DATA_TYPE_FUNDER_TYPE,
        DATA_TYPE_LICENSE_TYPE
    ]

    def __init__(
        self,
        data_id,
        data_type,
        uri='',
        label={},
        parent_ids=[],
        child_ids=[],
        has_children=False):

        super(ReferenceData, self).__init__(data_id, data_type)

        self.uri = uri
        self.label = label # { 'fi': 'value1', 'en': 'value2',..., 'default': 'default_value' }
        self.parent_ids = parent_ids # [ 'id1', 'id2', ... ]
        self.child_ids = child_ids # [ 'id1', 'id2', ... ]
        self.has_children = has_children # True or False

    def __str__(self):
        return (
            "{" +
                "\"id\":\"" + self.doc_id + "\","
                "\"type\":\"" + self.doc_type + "\","
                "\"uri\":\"" + self.uri + "\","
                "\"label\":\"" + str(self.label) + "\","
                "\"parent_ids\":\"" + str(self.parent_ids) + "\","
                "\"child_ids\":\"" + str(self.child_ids) + "\","
                "\"has_children\":\"" + str(self.has_children) + "\""
            "}")
