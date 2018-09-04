from service.service_utils import set_default_label

class IndexableData:
    '''
    Base class for any data that can be indexed into Metax Elasticsearch
    '''

    DATA_TYPE_ORGANIZATION = 'organization'

    def __init__(
        self,
        doc_id,
        doc_type,
        label,
        uri,
        same_as,
        scheme):

        self.doc_type = doc_type
        self.doc_id = self._create_es_document_id(doc_id)
        self.label = {} # { 'fi': 'value1', 'en': 'value2',..., 'und': 'default_value' }
        self.same_as = same_as
        self.code = doc_id

        if scheme:
            self.scheme = scheme
        else:
            self.scheme = 'https://metax.fairdata.fi/es/'
            self.scheme += 'organization_data/' if self.doc_type == IndexableData.DATA_TYPE_ORGANIZATION else 'reference_data/'
            self.scheme += self.doc_type + '/_search?pretty'

        # Replace quotes with corresponding html entity not to break outbound json
        if label:
            for key, val in label.items():
                self.label[key] = val.replace("'", "&quot;")

            set_default_label(self.label)
        else:
            self.label = {"und": self.code}

        self.uri = uri if uri else ''

    def to_es_document(self):
        return str(self)

    def get_es_document_id(self):
        return self.doc_id

    def _create_es_document_id(self, doc_id):
        return self.doc_type + "_" + doc_id
