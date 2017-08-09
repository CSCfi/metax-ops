import json
from domain.reference_data import ReferenceData

class LocalDataService:
    '''
    Service for getting reference data for elasticsearch index. The data is local,
    i.e. data should exist on localhost.
    '''

    LOCAL_REFDATA_FOLDER = 'resources/local-refdata/'

    def get_data(self, data_type):
        return self._parse_local_reference_data(data_type)

    def _parse_local_reference_data(self, data_type):
        index_data_models = []
        with open(self.LOCAL_REFDATA_FOLDER + data_type + '.json', 'r') as f:
            data = json.load(f)
            for item in data:
                same_as = item.get('same_as', [])
                label = item.get('label', '')
                uri = item.get('uri', '')
                data_id = item.get('id', '')
                index_data_models.append(ReferenceData(data_id, data_type, label, uri, same_as = same_as))

        # if len(index_data_models) > 0:
        #     for ref in index_data_models:
        #         print(ref, sep='\n\n')

        return index_data_models
