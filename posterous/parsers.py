# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

from posterous.models import ModelFactory
from posterous.utils import import_simplejson


class XMLParser(object):
    def __init__(self):
        pass

    def parse(self, method, payload):
        return None


class JSONParser(object):
    def __init__(self):
        self.json_lib = import_simplejson()

    def parse(self, method, payload):
        return None


class ModelParser(object):
    def __init__(self, model_factory=None):
        self.model_factory = model_factory or ModelFactory

    def parse(self, method, payload):
        # get the appropriate model for this payload
        try:
            if method.payload_type is None:
                return
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise Exception('No model for this payload type: %s' % 
                            method.payload_type)

        # parse the response
        if method.response_type == 'xml':
            # the xml parser will return json 
            xml_parser = XMLParser()
            data = xml_parser.parse(method, payload)
        else:
            json_parser = JSONParser()
            data = json_parser.parse(method, payload)

        if method.payload_list:
            result = model.parse_list(method.api, data)
        else:
            result = model.parse(method.api, data)

        return result
