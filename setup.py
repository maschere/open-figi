import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenFIGIClient",
    version="1.1.0",
    author="Leonardo Urbano",
    author_email="leonardo.urbano87@libero.it",
    description="A client to query OpenFIGI Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leourb/open-figi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
