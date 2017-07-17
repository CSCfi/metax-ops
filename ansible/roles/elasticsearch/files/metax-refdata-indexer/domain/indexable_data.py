from slugify import slugify

class IndexableData:
    '''
    Base class for any data that can be indexed into Metax Elasticsearch
    '''

    def __init__(
        self,
        doc_id,
        doc_type):

        self.doc_id = slugify(doc_id)
        self.doc_type = doc_type

    def to_es_document(self):
        return str(self)

    def get_es_document_id(self):
        return self.doc_id
