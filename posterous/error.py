# Copyright:
#    Copyright (c) 2010, Benjamin Reitzammer <http://github.com/nureineide>, 
#    All rights reserved.
#            
# License:
#    This program is free software. You can distribute/modify this program under
#    the terms of the Apache License Version 2.0 available at 
#    http://www.apache.org/licenses/LICENSE-2.0.txt 

class PosterousError(Exception):
    """Posterous exception"""
    def __init__(self, error, code=None):
        self.message = error
        self.error_code = error_code = code

    def __str__(self):
        return self.message

