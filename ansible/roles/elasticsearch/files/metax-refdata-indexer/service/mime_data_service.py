import json
import requests
import xml.etree.cElementTree as ET
import os
from domain.reference_data import ReferenceData
from service.service_utils import set_default_label

class MimeDataService:
    '''
    Service for getting mime type reference data for elasticsearch index. The data is in iana.org,
    so it is first fetched and parsed.
    '''

    MIME_TYPE_REFERENCE_DATA_SOURCE_URL  'https://www.iana.org/assignments/media-types/media-types.xml'
    MIME_TYPE_REGISTRY_IDS = [ 'application',
                                'audio'
                                'font'
                                'image',
                                'message',
                                'model',
                                'multipart',
                                'text',
                                'video']

    TEMP_XML_FILENAME = '/tmp/data.xml'

    def get_data(self, data_type):
        self._fetch_mime_data()
        index_data_models = self._parse_mime_data(data_type)
        os.remove(self.TEMP_XML_FILENAME)

        # i=0
        # while i < 10:
        #     print(index_data_models[i], sep='\n\n')
        #     i = i+1

        return index_data_models

    def _parse_mime_data(self, data_type):
        index_data_models = []
        print("Extracting relevant data from the fetched data")
        for event, elem in ET.iterparse(self.TEMP_XML_FILENAME, events=("start", "end")):
            if event == 'start':
                if elem.tag == 'registry' and elem.attrib['id'] in self.MIME_TYPE_REGISTRY_IDS:
                    is_parsing_model_elem = True
                elif is_parsing_model_elem and elem.tag == 'file' and elem.attrib['type'] == 'template':
                    label = {}
                    same_as = []
                    uri = 'https://www.iana.org/assignments/media-types/' + elem.text
                    label['fi'] == elem.text
                    label['en'] == elem.text
                    data_id = elem.text
            elif event == 'end':
                if elem.tag == 'registry':
                    is_parsing_model_elem = False
                elif is_parsing_model_elem and elem.tag == 'file':
                    set_default_label(label)
                    index_data_models.append(ReferenceData(data_id, data_type, uri, label, same_as=same_as))

        return index_data_models

    def _fetch_mime_data(self, data_type):
        url = self.MIME_TYPE_REFERENCE_DATA_SOURCE_URL
        print("Fetching data from url " + url)
        response = requests.get(url, stream=True)
        with open(self.TEMP_XML_FILENAME, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)
