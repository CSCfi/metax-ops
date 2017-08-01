import json
import requests
import os
from domain.reference_data import ReferenceData

class InfraDataService:
    '''
    Service for getting research infrastructure data for elasticsearch index. The data is in AVAA,
    so it is first fetched and parsed.
    '''

    INFRA_REFERENCE_DATA_SOURCE_URL = 'https://avaa.tdata.fi/api/jsonws/tupa-portlet.Infrastructures/get-all-infrastructures'

    TEMP_FILENAME = '/tmp/data.json'

    def get_data(self):
        self._fetch_infra_data()
        index_data_models = self._parse_infra_data()
        os.remove(self.TEMP_FILENAME)

        # i=0
        # while i < 10:
        #     print(index_data_models[i], sep='\n\n')
        #     i = i+1

        return index_data_models

    def _parse_infra_data(self):
        index_data_models = []

        print("Extracting relevant data from the fetched data")
        with open(self.TEMP_FILENAME, 'r') as f:
            data = json.load(f)
            for item in data:
                if item.get('urn', ''):
                    data_id = self._get_data_id(item['urn'])
                    data_type = ReferenceData.DATA_TYPE_RESEARCH_INFRA
                    uri = 'http://urn.fi/' + item['urn']
                    label = {}
                    if item.get('name_FI'):
                        label['fi'] = item['name_FI']
                        label['default'] = item['name_FI']
                    if item.get('name_EN'):
                        label['en'] = item['name_EN']

                    index_data_models.append(ReferenceData(data_id, data_type, uri=uri, label=label))

        return index_data_models

    def _fetch_infra_data(self):
        url = self.INFRA_REFERENCE_DATA_SOURCE_URL
        print("Fetching data from url " + url)
        response = requests.get(url, stream=True)
        with open(self.TEMP_FILENAME, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)

    def _get_data_id(self, urn):
        return urn.replace(':', '-')
