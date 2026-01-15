import os
from setuptools import setup, find_packages

VERSION = '1.0.0'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name='django-rest-framework-missedcall',
    version=VERSION,
    author='tabaro',
    author_email='contact@tabaro.io',
    description='A production-ready DRF gateway for ultra-cheap flash-call authentication.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/tabarochristian/drf-missed-call-auth',
    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=3.2',
        'djangorestframework>=3.12',
        'twilio>=7.0.0',
    ],
    python_requires='>=3.8',
    keywords='django rest-framework authentication missed-call flash-call twilio',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: Communications :: Telephony',
    ],
    project_urls={
        'Documentation': 'https://github.com/tabarochristian/drf-missed-call-auth#readme',
        'Source': 'https://github.com/tabarochristian/drf-missed-call-auth',
        'Tracker': 'https://github.com/tabarochristian/drf-missed-call-auth/issues',
    },
)