import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    readme = open(os.path.join(here, 'README.md')).read()
except IOError:
    readme = ''

setup_requires = [
    'nose>=1.3.0',
]

setup(
    name='detach',
    version='1.0',
    description="Fork and detach the current processe.",
    long_description=readme,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='fork daemon detach',
    author='Ryan Bourgeois',
    author_email='bluedragonx@gmail.com',
    url='https://github.com/bluedragonx/detach',
    license='BSD-derived',
    py_modules=['detach'],
    setup_requires=setup_requires,
    test_suite = 'nose.collector',
)
