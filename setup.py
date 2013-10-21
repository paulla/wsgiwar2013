import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_chameleon',
    'pyramid_fanstatic',
    'rebecca.fanstatic',
    'couchdbkit',
    'pyramid_beaker',
    'Babel',
    'lingua',
    'py-bcrypt',
    'js.bootstrap',
    'css.fontawesome',
    'pyramid_mailer',
    'pillow',
    'js.jquery',
    'fanstatic',
    'readability-lxml',
    ]

setup(name='wsgiwars',
      version='0.0',
      description='wsgiwars',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="wsgiwars",
      entry_points="""\
      [paste.app_factory]
      main = wsgiwars:main
      [console_scripts]
      setAdmin = wsgiwars.utils:setAdmin
      delAndPurge = wsgiwars.utils:delAndPurge
      coherence = wsgiwars.utils:coherence
      [fanstatic.libraries]
      wsgiwars = wsgiwars.resources:library
      """,
      )
