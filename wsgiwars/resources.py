from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group

from js.jquery import jquery

library = Library('resources', 'resources_src')

cssLink = Resource(library, 'link.css')

linkAjax_js = Resource(library, 'link.js', depends=[jquery, ])
linkAjax =  Group([linkAjax_js])
