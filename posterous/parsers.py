# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

import simplejson
from posterous.models import ModelFactory, attribute_map


def set_type(name, value):
    """Sets the value to the appropriate type."""
    for names in attribute_map:
        if name in names:
            return attribute_map.get(names)(value)
    # most likely a string
    return value


class JSONParser(object):
    def parse(self, payload):
        """Parses the JSON payload and returns a dict of objects"""
        json = simplejson.loads(payload)
        return json


class ModelParser(object):
    """Used for parsing a method response into a model object."""

    def __init__(self, model_factory=None):
        self.model_factory = model_factory or ModelFactory

    def parse(self, method, payload):
        print 'model parser'

        # Get the appropriate model for this payload
        if method.payload_type is None:
            return
        try:
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise Exception('No model for this payload type: %s' % 
                            method.payload_type)

        # Parse the response data and then create the model instance
        print 'parse payload'
        data = self._parse_payload(payload)
        print data
        return model.parse(method.api, data)

    def _parse_payload(self, payload):
        # Currently the only response type is JSON
        json_parser = JSONParser()
        return json_parser.parse(payload)
