import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="macusers",
    version="0.0.3",
    author="Bryan Heinz",
    author_email="pypi@bryanheinz.com",
    description="Get the macOS console username and/or a list of local non-system users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bryanheinz/python-macusers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
)
