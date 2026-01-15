"""
Setup script for django-rest-framework-missedcall

For modern installation, use pyproject.toml.
This file is kept for backward compatibility.
"""
from setuptools import setup, find_packages

# Read version from package
VERSION = '2.0.0'

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-rest-framework-missedcall',
    version=VERSION,
    author='tabaro',
    author_email='contact@tabaro.io',
    description='Production-grade flash-call authentication for Django REST Framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tabaro/django-rest-framework-missedcall',
    project_urls={
        'Documentation': 'https://github.com/tabaro/django-rest-framework-missedcall#readme',
        'Bug Tracker': 'https://github.com/tabaro/django-rest-framework-missedcall/issues',
        'Source Code': 'https://github.com/tabaro/django-rest-framework-missedcall',
        'Changelog': 'https://github.com/tabaro/django-rest-framework-missedcall/blob/main/CHANGELOG.md',
    },
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'django>=3.2',
        'djangorestframework>=3.12',
        'twilio>=7.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-django>=4.5',
            'coverage>=7.0',
            'black>=23.0',
            'flake8>=6.0',
            'mypy>=1.0',
            'isort>=5.12',
            'pre-commit>=3.0',
        ],
        'redis': [
            'redis>=4.5',
            'django-redis>=5.2',
        ],
        'postgres': [
            'psycopg2-binary>=2.9',
        ],
        'full': [
            'redis>=4.5',
            'django-redis>=5.2',
            'psycopg2-binary>=2.9',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: Communications :: Telephony',
    ],
    keywords='django rest-framework authentication missed-call flash-call twilio phone-verification otp-alternative',
    zip_safe=False,
)