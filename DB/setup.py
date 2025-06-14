import pathlib
from setuptools import setup, find_packages
 
HERE = pathlib.Path(__file__).parent.resolve()
 
PACKAGE_NAME = "DB"
AUTHOR = "Athena Chuang"
AUTHOR_EMAIL = "athenajc@gmail.com"
URL = "hhttps://github.com/athenajc/DB"
DOWNLOAD_URL = "https://pypi.org/project/DB/"
 
LICENSE = "MIT"
VERSION = "1.0.0"
DESCRIPTION = "A set of sql tools in Python"
LONG_DESCRIPTION = (HERE / "docs" / "README.md").read_text(encoding="utf8")
LONG_DESC_TYPE = "text/markdown"
 

CLASSIFIERS = [f"Programming Language :: Python :: 3.{str(v)}" for v in range(8, 12)]
PYTHON_REQUIRES = ">=3.8"
 
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
)
