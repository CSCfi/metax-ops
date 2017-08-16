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

    DATA_TYPE_MIME_TYPE = 'mime_type'

    DATA_TYPE_ACCESS_TYPE = 'access_type'
    DATA_TYPE_CHECKSUM_ALGORITHM = 'checksum_algorithm'
    DATA_TYPE_RESOURCE_TYPE = 'resource_type'
    DATA_TYPE_IDENTIFIER_TYPE = 'identifier_type'
    DATA_TYPE_ACCESS_RESTRICTION_GROUNDS_TYPE = 'access_restriction_grounds_type'
    DATA_TYPE_CONTRIBUTOR_ROLE = 'contributor_role'
    DATA_TYPE_FUNDER_TYPE = 'funder_type'
    DATA_TYPE_LICENSES = 'license'

    FINTO_REFERENCE_DATA_TYPES = [
        DATA_TYPE_FIELD_OF_SCIENCE,
        DATA_TYPE_LANGUAGE,
        DATA_TYPE_LOCATION,
        DATA_TYPE_KEYWORD
    ]

    LOCAL_REFERENCE_DATA_TYPES = [
        DATA_TYPE_ACCESS_TYPE,
        DATA_TYPE_CHECKSUM_ALGORITHM,
        DATA_TYPE_RESOURCE_TYPE,
        DATA_TYPE_IDENTIFIER_TYPE,
        DATA_TYPE_ACCESS_RESTRICTION_GROUNDS_TYPE,
        DATA_TYPE_CONTRIBUTOR_ROLE,
        DATA_TYPE_FUNDER_TYPE,
        DATA_TYPE_LICENSES
    ]

    def __init__(
        self,
        data_id,
        data_type,
        label,
        uri,
        parent_ids=[],
        child_ids=[],
        same_as=[]):

        super(ReferenceData, self).__init__(data_id, data_type, label, uri)

        self.parent_ids = []
        self.child_ids = []
        self.has_children = False
        self.same_as = same_as

        if len(parent_ids) > 0:
            self.parent_ids = [self._create_es_document_id(p_id) for p_id in parent_ids]
        if len(child_ids) > 0:
            self.child_ids = [self._create_es_document_id(c_id) for c_id in child_ids]

        if len(child_ids) > 0:
            self.has_children = True

    def __str__(self):
        return (
            "{" +
                "\"id\":\"" + self.get_es_document_id() + "\","
                "\"type\":\"" + self.doc_type + "\","
                "\"uri\":\"" + self.uri + "\","
                "\"label\":\"" + str(self.label) + "\","
                "\"parent_ids\":\"" + str(self.parent_ids) + "\","
                "\"child_ids\":\"" + str(self.child_ids) + "\","
                "\"has_children\":\"" + str(self.has_children) + "\","
                "\"same_as\":\"" + str(self.same_as) + "\""
            "}")
