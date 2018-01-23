# -*- coding: utf-8 -*-

from os.path import abspath
from os.path import dirname
from os.path import join
from setuptools import find_packages
from setuptools import setup
import codecs

import erudit


def read_relative_file(filename):
    """
    Returns contents of the given file, whose path is supposed relative
    to this module.
    """
    with codecs.open(join(dirname(abspath(__file__)), filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='erudit-core',
    version=erudit.__version__,
    author='Érudit Consortium',
    author_email='tech@erudit.org',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/erudit/erudit-core',
    license='GPLv3',
    description='A Django application that defines the core entities of the Érudit platform.',
    long_description=read_relative_file('README.rst'),
    zip_safe=False,
    install_requires=[
        'django>=1.10,<2.0',
        'django-polymorphic>=0.9,<2.0',
        'django-taggit>=0.20',
        'eulfedora>=1.5.0',
        'lxml>=3.6.0',
        'nameparser>=0.5.0',
        'Pillow>=3.2.0',
        'Sickle>=0.6',
        'structlog>=17.2.0',
        # Érudit modules
        'liberuditarticle',
        # temporarily fetching from git until 0.13 is released. Otherwise,
        # test_published_issues_uses_fedora_order fails.
        'django-modeltranslation==0.13',
    ],
    dependency_links=[
        'git+https://github.com/erudit/liberuditarticle.git#egg=liberuditarticle-0.2.8',
        'git+https://github.com/deschler/django-modeltranslation.git@00fc7f1804aaa1b1e37af48e67871080851e14b0#egg=django-modeltranslation-0.13', # noqa
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: French',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
