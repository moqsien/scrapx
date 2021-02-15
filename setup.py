from os.path import dirname, join
from pkg_resources import parse_version
from setuptools import setup, find_packages, __version__ as setuptools_version


with open(join(dirname(__file__), 'scrapx/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


def has_environment_marker_platform_impl_support():
    """Code extracted from 'pytest/setup.py'
    https://github.com/pytest-dev/pytest/blob/7538680c/setup.py#L31

    The first known release to support environment marker with range operators
    it is 18.5, see:
    https://setuptools.readthedocs.io/en/latest/history.html#id235
    """
    return parse_version(setuptools_version) >= parse_version('18.5')


install_requires = [
    'scrapy>=2.4.1',
    'pymongo>=3.11.2',
]
extras_require = {}
cpython_dependencies = [
    'lxml>=3.5.0',
    'PyDispatcher>=2.0.5',
]
if has_environment_marker_platform_impl_support():
    extras_require[':platform_python_implementation == "CPython"'] = cpython_dependencies
    extras_require[':platform_python_implementation == "PyPy"'] = [
        # Earlier lxml versions are affected by
        # https://foss.heptapod.net/pypy/pypy/-/issues/2498,
        # which was fixed in Cython 0.26, released on 2017-06-19, and used to
        # generate the C headers of lxml release tarballs published since then, the
        # first of which was:
        'lxml>=4.0.0',
        'PyPyDispatcher>=2.1.0',
    ]
else:
    install_requires.extend(cpython_dependencies)


setup(
    name='Scrapx',
    version=version,
    url='https://github.com/moqsien/scrapx',
    project_urls={
        'Documentation': 'https://github.com/moqsien/scrapx/blob/main/README.md',
        'Source': 'https://github.com/moqsien/scrapx',
        'Tracker': 'https://docs.scrapy.org/',
    },
    description='A customized version of Scrapy',
    long_description=open('DESCRIPTION.rst').read(),
    author='MoQsien',
    maintainer='MoQsien',
    maintainer_email='moqsien@foxmail.com',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*', 'example')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['scrapx = scrapx.cmdline:execute']
    },
    classifiers=[
        'Framework :: Scrapx',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
    extras_require=extras_require,
)
