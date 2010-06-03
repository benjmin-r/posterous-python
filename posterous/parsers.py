# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

import xml.etree.cElementTree as ET

from posterous.models import ModelFactory, attribute_map
from posterous.utils import import_simplejson
from posterous.error import PosterousError


def set_type(name, value):
    """Sets the value to the appropriate type."""
    for names in attribute_map:
        if name in names:
            return attribute_map.get(names)(value)
    # most likely a string
    return value

 
class XMLDict(dict):
    """
    Traverses the XML tree recursively and builds an object 
    representation of each element. Element attributes are not
    read since they don't appear in any current Posterous API
    response. Returns a dictionary of objects.

    Modified from: http://code.activestate.com/recipes/410469/
    """
    def __init__(self, parent_element):
        childrenNames = list((child.tag for child in parent_element))

        for element in parent_element:
            tag = element.tag.lower()
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    # we assume that if the first two tags in a series are 
                    # different, then they are all different.
                    aDict = XMLDict(element)
                else:
                    # treat like list 
                    aDict = {element[0].tag.lower(): XMLList(element)}
                
                if childrenNames.count(tag) > 1:
                    # there are multiple siblings with this tag, so they 
                    # must be grouped together
                    try:
                        # move this element's dict under the first sibling
                        self[tag].append(aDict)
                    except KeyError:
                        # the first for this tag
                        self.update({tag: [aDict]})
                else:
                    self.update({tag: aDict})
            else:
                # finally, if there are no child tags, extract the text
                value = set_type(tag, element.text.strip()) 
                self.update({tag: value})


class XMLList(list):
    """
    Similar to the XMLDict class; traverses a list of element
    siblings and creates a list of their values.

    Modified from: http://code.activestate.com/recipes/410469/
    """
    def __init__(self, aList):
        for element in aList:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XMLDict(element))
                else:
                    self.append(XMLList(element))
            elif element.text:
                text = set_type(element.tag.lower(), element.text.strip())
                if text:
                    self.append(text)


class XMLParser(object):
    def __init__(self):
        pass

    def parse(self, method, payload):
        """Parses the XML payload and returns a dict of objects"""
        root = ET.XML(payload)
        
        if root.tag != 'rsp':
            raise PosterousError('XML response is missing the status tag! ' \
                                 'The response may be malformed.')
        
        # Verify that the response was successful before parsing
        if root.get('stat') == 'fail':
            error = root[0]
            self.parse_error(error)
        else:
            # There are nesting inconsistencies in the response XML 
            # with some tags appearing below the payload model element. 
            # This is a problem when the payload_type is _not_ a list.
            # If the root has multiple children, all siblings of the first
            # child will be moved under said child.
            if not method.payload_list and len(root) > 1:
                for node in root[1:]:
                    root[0].append(node)
                    root.remove(node)
            
            if method.payload_list:
                # A list of results is expected
                result = []
                for node in root:
                    result.append(XMLDict(node))
            else:
                # Move to the first child before parsing the tree
                result = XMLDict(root[0])
            
            # Make sure the values are formatted properly
            return self.cleanup(result)

    def parse_error(self, error):
        raise PosterousError(error.get('msg'), error.get('code'))
    
    def cleanup(self, output):
        def clean(obj):
            if 'comment' in obj:
                comments = obj['comment']
                del obj['comment']
                # make it a list
                if not isinstance(comments, list):
                    comments = [comments]
                obj['comments'] = comments

            if 'media' in obj:
                # make it a list
                if not isinstance(obj['media'], list):
                    obj['media'] = [obj['media']]
            return obj

        if isinstance(output, list):
            output = list((clean(obj) for obj in output))
        else: 
            output = clean(output)
        
        return output


class ModelParser(object):
    """Used for parsing a method response into a model object."""

    def __init__(self, model_factory=None):
        self.model_factory = model_factory or ModelFactory

    def parse(self, method, payload):
        # Get the appropriate model for this payload
        try:
            if method.payload_type is None:
                return
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise Exception('No model for this payload type: %s' % 
                            method.payload_type)

        # The payload XML must be parsed into a dict of objects before
        # being used in the model.
        if method.response_type == 'xml':
            xml_parser = XMLParser()
            data = xml_parser.parse(method, payload)
        else:
            raise NotImplementedError

        return model.parse(method.api, data)

