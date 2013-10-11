from fanstatic import Library
from fanstatic import Resource

from js.jquery import jquery

wsgiwarLibrary = Library('resources', 'resources_src')

linkAjax = Resource(wsgiwarLibrary, 'link.js', depends=[jquery, ])
