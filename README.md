# OpenFIGI Python Client

## Abstract

OpenFIGI is an open source service which maintains and provides updated Bloomberg identifiers for almost all the 
securities which have an ISIN or another market identifier. More information can be 
found [here](https://www.openfigi.com/about/aboutus)

## Usage

The package is very easy to use. After the installation you can use it as it follows:

```python
OpenFIGI("ID_ISIN", ["ISIN1", "ISIN2", "ISIN3", ...])
```

As soon as you run it you will be prompted to input your API key (please make sure you insert it correctly as there is
no check on its validity!).

If the API key typed is valid, a request will be submitted to the OpenFIGI database and the results will be parsed.

The class returns the raw data in a JSON format. However, other results formats are available like `pandas.DataFrame` 
and Microsoft Excel

The package will also take care of the limitation in time requests and size of each request automatically. 
It uses a multithreading queue which allows the user to optimize the time and the time resources needed to query 
thousands of set of identifiers.

Please find as it follows an example
```python
from pprint import pprint

from openfigi import OpenFIGI

data = OpenFIGI("ID_ISIN", ["US0378331005"]) # Let's query the Bloomberg identifiers for Apple Inc. given its ISIN
pprint(data.to_df())
```

We could also export the results in Excel, leveraging `pandas` by doing so:

```python
from openfigi import OpenFIGI

data = OpenFIGI('ID_ISIN', ["US0378331005"])
data.get_results_to_excel("my_results.xlsx")  # If nothing is passed then the file will be saved as results.xlsx
```

The results will also be automatically saved in a `pickle` in the same dir as your package (they will be overwritten 
each time so make sure you save your last query)

In case of big requests, the package will automatically save the preliminary results in `pickle` every 10 chunks of
workers processed. This will be useful in case of a timeout error or any other issue which may happen while querying
big amount of data.

The pickled data can be easily recovered using the **Utility** class with the following command:

```python
import pandas as pd

from openfigi import Utility

data = Utility.from_pickle("OpenFIGI")  # Default name used by the OpenFIGI class (please omit the .pickled extension)
```

## Contacts

Feel free to contact me or to drop a comment if you have issues or suggestions.
