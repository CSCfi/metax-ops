import json
from elasticsearch import Elasticsearch

class ElasticSearchService:
    '''
    Service for operating with Elasticsearch APIs. Used when data indices are created/deleted and
    data is deleted/reindexed.
    '''

    ES_CONFIG_DIR = 'resources/es-config/'

    REFERENCE_DATA_INDEX_NAME = 'reference_data'
    REFERENCE_DATA_INDEX_FILENAME = ES_CONFIG_DIR + 'reference_data_index.json'
    REFERENCE_DATA_TYPE_MAPPING_FILENAME = ES_CONFIG_DIR + 'reference_data_type_mapping.json'

    ORGANIZATION_DATA_INDEX_NAME = 'organization_data'
    ORGANIZATION_DATA_INDEX_FILENAME = ES_CONFIG_DIR + 'organization_data_index.json'
    ORGANIZATION_DATA_TYPE_MAPPING_FILENAME = ES_CONFIG_DIR + 'organization_data_type_mapping.json'

    def __init__(self):
        self.es = Elasticsearch(
            [
            'http://localhost:9200/'
            ]
        )

    def index_exists(self, index):
        return self.es.indices.exists(index=index)

    def create_index(self, index, filename):
        print("Trying to create index " + index)
        return self._operation_ok(self.es.indices.create(index=index,body=self._get_json_file_as_str(filename)))

    def delete_index(self, index):
        print("Trying to delete index " + index)
        return self._operation_ok(self.es.indices.delete(index=index, ignore=[404]))

    def create_type_mapping(self, index, doc_type, filename):
        print("Trying to create mapping type " + doc_type + " for index " + index)
        return self._operation_ok(self.es.indices.put_mapping(index=index, doc_type=doc_type, body=self._get_json_file_as_str(filename)))

    def delete_and_update_indexable_data(self, index, doc_type, indexable_data_list):
        if len(indexable_data_list) > 0:
            self._delete_all_documents_from_index_with_type(index, doc_type)
            bulk_update_str = "\n".join(map(lambda idx_data: self._create_bulk_update_row_for_indexable_data(index, doc_type, idx_data), indexable_data_list))
            print("Trying to bulk update reference data with type " + doc_type + " to index " + index)
            return self._operation_ok(self.es.bulk(body=bulk_update_str, request_timeout=30))
        return None

    def _delete_all_documents_from_index(self, index):
        print("Trying to delete all documents from index " + index)
        return self._operation_ok(self.es.delete_by_query(index=index, body="{\"query\": { \"match_all\": {}}}"))

    def _delete_all_documents_from_index_with_type(self, index, doc_type):
        print("Trying to delete all documents from index " + index + " having type " + doc_type)
        return self._operation_ok(self.es.delete_by_query(index=index, doc_type=doc_type, body="{\"query\": { \"match_all\": {}}}"))

    def _create_bulk_update_row_for_indexable_data(self, index, doc_type, indexable_data_item):
        return "{\"index\":{\"_index\": \"" + index + "\", \"_type\": \"" + doc_type + "\", \"_id\":\"" + indexable_data_item.get_es_document_id() + "\"}}\n" + indexable_data_item.to_es_document()

    def _create_bulk_delete_row_indexable_data(self, index, doc_type, indexable_data_item):
       return "{\"delete\":{\"_index\": \"" + index + "\", \"_type\": \"" + doc_type + "\", \"_id\":\"" + indexable_data_item.get_es_document_id() + "\"}}"

    def _operation_ok(self, op_response):
        if op_response.get('acknowledged'):
            print("OK")
            return True
        return False

    def _get_json_file_as_str(self, filename):
        with open(filename) as json_data:
            return json.load(json_data)
