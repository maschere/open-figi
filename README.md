# open-figi

## Abstract

OpenFIGI is an open source service which maintains and provides updated Bloomberg identifiers for almost all the securities which have an ISIN or another market identifier. More information can be found (here)[https://www.openfigi.com/about/aboutus]

## Usage

The package is very easy to use. After the installation you can use it as it follows:

`OpenFIGI("ID_ISIN", ["ISIN1", "ISIN2", "ISIN3", ...])`

The class returns the raw data in a JSON format. However, other results formats are available like `pandas.DataFrame` and Microsoft Excel

The package will also take care of the limitation in time requests and size of each request automatically. It uses a multithreading queue which allows the user to optimize the time and the time resources needed to query thousands of set of identifiers.
