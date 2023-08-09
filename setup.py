from setuptools import setup, find_packages
import codecs


def read_file(path: str) -> "list[str]":
    with codecs.open(path, 'r', 'utf-8') as f:
        return [l.strip() for l in f.readlines()]


README_PATH = 'README.md'
DESCRIPTION = 'A Google Photos API wrapper library'
VERSION = "0.1.0"
LONG_DESCRIPTION = '\n'.join(read_file(README_PATH))
requirements = read_file("./requirements/publish.txt")
setup(
    name="gp_wrapper",
    version=VERSION,
    author="danielnachumdev",
    author_email="<danielnachumdev@gmail.com>",
    description=DESCRIPTION,
    long_description=open('README.md', "r", encoding="utf8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/danielnachumdev/gp_wrapper',
    license="MIT License",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "archive/"]),
    install_requires=[""],
    platforms=["All"],
    keywords=['functions', 'decorators', 'methods', 'classes', 'metaclasses'],
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
