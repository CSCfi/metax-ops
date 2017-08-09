from service.service_utils import set_default_label

class IndexableData:
    '''
    Base class for any data that can be indexed into Metax Elasticsearch
    '''

    def __init__(
        self,
        doc_id,
        doc_type,
        label,
        uri):

        self.doc_type = doc_type
        self.doc_id = self._create_es_document_id(doc_id)
        self.label = label if label else '' # { 'fi': 'value1', 'en': 'value2',..., 'default': 'default_value' }
        set_default_label(label)
        self.uri = uri if uri else ''

    def to_es_document(self):
        return str(self)

    def get_es_document_id(self):
        return self.doc_id

    def _create_es_document_id(self, doc_id):
        return self.doc_type + "_" + doc_id
