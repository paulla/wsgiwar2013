############################################################################
# The MIT License (MIT)
#
# Copyright (c) 2013 PauLLA
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNES FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
############################################################################

""" PauLLA WSGI Wrestle 2013 Delicious like
"""

class LoggedPredicate(object):
    """
    """

    def __init__(self, val, config):
        self._val = val

    def text(self):
        return 'predicat on login'

    phash = text

    def __call__(self,  context, request):
        return ('login' in request.session) == self._val

class Is_AdminPredicate(object):
    """
    """

    def __init__(self, val, config):
        self._val = val

    def text(self):
        return 'predicat on admin'

    phash = text

    def __call__(self,  context, request):
        return ('is_admin' in request.session and \
                              request.session['is_admin']) == self._val
