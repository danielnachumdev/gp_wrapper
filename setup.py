import codecs
from setuptools import setup, find_packages


def read_file(path: str) -> "list[str]":
    with codecs.open(path, 'r', 'utf-8') as f:
        return [l.strip() for l in f.readlines()]


README_PATH = 'README.md'
DESCRIPTION = 'A Google Photos API wrapper library'
VERSION = "0.8.2"
LONG_DESCRIPTION = '\n'.join(read_file(README_PATH))
PACKAGE = "gp_wrapper"
setup(
    name=PACKAGE,
    version=VERSION,
    author="danielnachumdev",
    author_email="<danielnachumdev@gmail.com>",
    description=DESCRIPTION,
    long_description=open('README.md', "r", encoding="utf8").read(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/danielnachumdev/{PACKAGE}',
    license="MIT License",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "archive/"]),
	install_requires=['google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'danielutils', 'requests', 'tqdm'],  #noqa
    keywords=['functions', 'methods', 'classes', 'API'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        # "Operating System :: Unix",
        # "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
# python .\setup.py sdist
# twine upload dist/...
