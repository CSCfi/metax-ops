import json
import requests
import xml.etree.cElementTree as ET
import os
from domain.reference_data import ReferenceData

class FintoDataService:
    '''
    Service for getting reference data for elasticsearch index. The data is in Finto,
    so it is first fetched and parsed.
    '''


    SKOS_NS = '{http://www.w3.org/2004/02/skos/core#}'
    RDF_NS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
    XML_NS = '{http://www.w3.org/XML/1998/namespace}'
    LVONT_NS = '{http://lexvo.org/ontology#}'

    FINTO_REFERENCE_DATA_SOURCE_URLS = {
        ReferenceData.DATA_TYPE_FIELD_OF_SCIENCE: 'http://finto.fi/rest/v1/okm-tieteenala/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_LANGUAGE: 'http://finto.fi/rest/v1/lexvo/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_LOCATION: 'http://finto.fi/rest/v1/yso-paikat/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_KEYWORD: 'http://finto.fi/rest/v1/yso/data?format=application/rdf%2Bxml'
    }

    FINTO_MODEL_ELEM = {
        ReferenceData.DATA_TYPE_FIELD_OF_SCIENCE: SKOS_NS + 'Concept',
        ReferenceData.DATA_TYPE_LANGUAGE: LVONT_NS + 'Language',
        ReferenceData.DATA_TYPE_LOCATION: SKOS_NS + 'Concept',
        ReferenceData.DATA_TYPE_KEYWORD: SKOS_NS + 'Concept'
    }

    TEMP_XML_FILENAME = '/tmp/data.xml'

    def get_data(self, data_type):
        self._fetch_finto_data(data_type)
        index_data_models = self._parse_finto_data(data_type)
        os.remove(self.TEMP_XML_FILENAME)

        # i=0
        # while i < 10:
        #     print(index_data_models[i], sep='\n\n')
        #     i = i+1

        return index_data_models

    def _parse_finto_data(self, data_type):
        index_data_models = []
        model_elem = self.FINTO_MODEL_ELEM[data_type]

        print("Extracting relevant data from the fetched data")
        is_parsing_model_elem = False
        for event, elem in ET.iterparse(self.TEMP_XML_FILENAME, events=("start", "end")):
            if event == 'start':
                if elem.tag == model_elem:
                    is_parsing_model_elem = True
                    uri = elem.attrib[self.RDF_NS + 'about']
                    label = {}
                    parent_ids = []
                    child_ids = []
                    has_children = False
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'prefLabel':
                    label[elem.attrib[self.XML_NS + 'lang']] = elem.text
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'broader':
                    parent_ids.append(self._get_data_id(data_type, self._get_uri_end_part(elem.attrib[self.RDF_NS + 'resource'])))
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'narrower':
                    child_ids.append(self._get_data_id(data_type, self._get_uri_end_part(elem.attrib[self.RDF_NS + 'resource'])))
            elif event == 'end' and elem.tag == model_elem:
                is_parsing_model_elem = False
                if(len(child_ids) > 0):
                    has_children = True

                if len(label) > 0:
                    if 'fi' in label:
                        label['default'] = label['fi']
                    elif 'en' in label:
                        label['default'] = label['en']
                    else:
                        label['default'] = next(iter(label.values()))

                data_id = self._get_data_id(data_type, self._get_uri_end_part(uri))
                index_data_models.append(ReferenceData(data_id,
                                                        data_type,
                                                        uri,
                                                        label,
                                                        parent_ids,
                                                        child_ids,
                                                        has_children))

        return index_data_models

    def _fetch_finto_data(self, data_type):
        url = self.FINTO_REFERENCE_DATA_SOURCE_URLS[data_type]
        print("Fetching data from url " + url)
        response = requests.get(url, stream=True)
        with open(self.TEMP_XML_FILENAME, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)


    def _get_uri_end_part(self, uri):
        return uri[uri.rindex('/')+1:].strip()

    def _get_data_id(self, part1, part2):
        return part1 + "-" + part2
