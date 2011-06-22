import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-reader",
    version = "0.2",
    url = '',
    license = 'BSD',
    description = "Simple RSS feed reader.",
    long_description = read('README'),

    author = 'Joshua Williams',
    author_email = 'jowillia@gmail.com',

    packages = ['reader'],
    package_dir = {'': 'src'},

    install_requires = ['setuptools'],

    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
