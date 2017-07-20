from domain.indexable_data import IndexableData

class ReferenceData(IndexableData):
    '''
    Model class for reference data that can be indexed into Metax Elasticsearch
    '''

    DATA_TYPE_FIELD_OF_SCIENCE = 'field_of_science'
    DATA_TYPE_LANGUAGE = 'language'
    DATA_TYPE_LOCATION = 'location'
    DATA_TYPE_KEYWORD = 'keyword'

    DATA_TYPE_ACCESS_TYPE = 'access_type'
    DATA_TYPE_CHECKSUM_TYPE = 'checksum_type'
    DATA_TYPE_DATACITE_FILE_TYPE = 'datacite_file_type'
    DATA_TYPE_MIME_TYPE = 'mime_type'
    DATA_TYPE_PID_TYPE = 'pid_type'
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
        DATA_TYPE_CHECKSUM_TYPE,
        DATA_TYPE_DATACITE_FILE_TYPE,
        DATA_TYPE_MIME_TYPE,
        DATA_TYPE_PID_TYPE,
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
        broader_ids=[],
        narrower_ids=[],
        has_narrower=False):

        super(ReferenceData, self).__init__(data_id, data_type)

        self.uri = uri
        self.label = label # { 'fi': 'value1', 'en': 'value2',..., 'default': 'default_value' }
        self.broader_ids = broader_ids # [ 'id1', 'id2', ... ]
        self.narrower_ids = narrower_ids # [ 'id1', 'id2', ... ]
        self.has_narrower = has_narrower # True or False

    def __str__(self):
        return (
            "{" +
                "\"id\":\"" + self.doc_id + "\","
                "\"type\":\"" + self.doc_type + "\","
                "\"uri\":\"" + self.uri + "\","
                "\"label\":\"" + str(self.label) + "\","
                "\"broader_ids\":\"" + str(self.broader_ids) + "\","
                "\"narrower_ids\":\"" + str(self.narrower_ids) + "\","
                "\"has_narrower\":\"" + str(self.has_narrower) + "\""
            "}")
