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
