import json
from domain.reference_data import ReferenceData

class LocalDataService:
    '''
    Service for getting reference data for elasticsearch index. The data is local,
    i.e. data should exist on localhost.
    '''

    FILE_TYPE_TXT = 'txt'
    FILE_TYPE_JSON = 'json'

    LOCAL_REFERENCE_DATA_FILE_FORMAT = {
        ReferenceData.DATA_TYPE_ACCESS_TYPE: FILE_TYPE_JSON,
        ReferenceData.DATA_TYPE_CHECKSUM_TYPE: FILE_TYPE_TXT,
        ReferenceData.DATA_TYPE_DATACITE_FILE_TYPE: FILE_TYPE_TXT,
        ReferenceData.DATA_TYPE_MIME_TYPE: FILE_TYPE_TXT,
        ReferenceData.DATA_TYPE_PID_TYPE: FILE_TYPE_TXT,
        ReferenceData.DATA_TYPE_ACCESS_RESTRICTION_GROUNDS_TYPE: FILE_TYPE_JSON,
        ReferenceData.DATA_TYPE_CONTRIBUTOR_ROLE_TYPE: FILE_TYPE_TXT,
        ReferenceData.DATA_TYPE_FUNDER_TYPE: FILE_TYPE_JSON,
        ReferenceData.DATA_TYPE_LICENSE_TYPE: FILE_TYPE_JSON
    }

    LOCAL_REFDATA_FOLDER = 'resources/local-refdata/'

    def get_data(self, data_type):
        return self._parse_local_reference_data(data_type)

    def _parse_local_reference_data(self, data_type):
        index_data_models = []
        file_format = self.LOCAL_REFERENCE_DATA_FILE_FORMAT[data_type]
        with open(self.LOCAL_REFDATA_FOLDER + data_type + '.' + file_format, 'r') as f:
            if file_format == self.FILE_TYPE_TXT:
                index_data_models = [ReferenceData(line.strip(), data_type, label={'default': line.strip()}) for line in f.readlines()]
            elif file_format == self.FILE_TYPE_JSON:
                data = json.load(f)
                for item in data:
                    label = {}
                    uri = ''
                    for key, value in item['label'].items():
                        label[key] = value
                    if item.get('url', ''):
                        uri = item['url']
                    index_data_models.append(ReferenceData(item['id'], data_type, label=label, uri=uri))

        # if len(index_data_models) > 0:
        #     for ref in index_data_models:
        #         print(ref, sep='\n\n')

        return index_data_models
