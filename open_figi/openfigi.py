"""OpenFIGI Module"""

import pickle
import requests
import urllib3

import numpy as np
import pandas as pd

from json import decoder
from queue import Queue
from threading import Thread

urllib3.disable_warnings()

# jobs = [
#     {'id_type': 'ID_ISIN', 'id_value': 'US4592001014'},
#     {'id_type': 'ID_WERTPAPIER', 'id_value': '851399', 'exchCode': 'US'},
#     {'id_type': 'ID_BB_UNIQUE', 'id_value': 'EQ0010080100001000', 'currency': 'USD'},
#     {'id_type': 'ID_SEDOL', 'id_value': '2005973', 'micCode': 'EDGX', 'currency': 'USD'}
# ]
#
# More reference at: https://www.openfigi.com/api#post-v2-mapping

MULTITHREADING = {
    'num_threads': 3
}

OPENFIGI = {
    'api_key': 'MY_API_KEY',
    'url': 'https://api.openfigi.com/v2/mapping',
    'api_limit': 100,
    'time_sleep': 2,  # seconds
    'json_fields': ["figi", "name", "ticker", "exchCode", "compositeFIGI", "uniqueID", "securityType",
                    "marketSector", "shareClassFIGI", "uniqueIDFutOpt", "securityType2", "securityDescription"]
}

PROXY = {
    'http': "",
    'https': ""
}


class Utility:
    """Collection of utility functions"""

    @staticmethod
    def to_pickle(object_name, filename):
        """
        Save an object to pickle
        :param object_name: an object in memory to be saved
        :param str filename: a filename where to save the object
        :return: a .pickled file with the binary data of the object
        """
        pickle.dump(object_name, open(f"{filename}.pickled", "wb"))

    @staticmethod
    def from_pickle(filename):
        """
        Read the data from a pickled file
        :param str filename: filename of the object to be read from
        :return: an in-memory binary object
        """
        return pickle.load(open(f"{filename}.pickled", "rb"))

    @staticmethod
    def split_list_in_n_chunks(l, n):
        """
        Split a list in N chunks
        :param list l: list to be slit
        :param int n: number of elements within each chunk
        :return: a list of iterators with the index of the split list
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]


class OpenFIGI:
    """OpenFIGI class to retrieve information from Bloomberg"""

    def __init__(self, id_type, id_value):
        """
        Initialize the class retrieving the data needed to run the script
        :param str id_type: type of ID - https://www.openfigi.com/api#v2-idType-values
        :param list id_value: list of identifiers (coherent with the above parameters - i.e. if idType is "ID_ISIN" this
        parameter MUST be a list of ISINs!)
        """
        self._open_figi_api_limit = OPENFIGI.get("api_limit")
        self.id_id_value = id_value
        if len(id_value) > self._open_figi_api_limit:
            self._id_value_list = Utility.split_list_in_n_chunks(id_value, self._open_figi_api_limit)
        else:
            self._id_value_list = [id_value]
        self._id_type = id_type
        self._url = OPENFIGI.get("url")
        self._api = OPENFIGI.get("api_key")
        self._job_list = self._build_job_list()
        self._queue = self._populate_queue()
        self._results = dict()
        self._run_multithreading()
        self._results_extended = self._extended_results()
        self._to_df = self.to_df()

    def _build_job_list(self):
        """
        Build a formatted job list starting from a list of identifiers
        :return: a 2-D array with maximum 25,000 elements of dictionaries to be sent to OpenFIGI
        """
        list_of_jobs = list()
        for i in self._id_value_list:
            job_list = list()
            for j in i:
                temp_obj = {'idType': self._id_type, 'idValue': j}
                job_list.append(temp_obj)
            list_of_jobs.append(job_list)
        return list_of_jobs

    def _send_request(self):
        """
        Send the list of jobs to OpenFIGI
        :return: populates the class member self.results with either a valid array from a response or an error message
        """
        while not self._queue.empty():
            work = self._queue.get()
            chunk = work[1]
            if work[0] % 10 == 0:
                Utility.to_pickle(self._results, "OpenFIGI")
                print("A pickle of the results has been correctly saved.")
            print(f"Thread {work[0]} of {len(self._job_list)} started. Querying OpenFIGI...")
            openfigi_headers = dict()
            openfigi_headers['Content-Type'] = 'text/json'
            openfigi_headers['X-OPENFIGI-APIKEY'] = OPENFIGI.get("api_key")
            try:
                response = requests.post(url=self._url, headers=openfigi_headers,
                                         json=chunk, proxies=PROXY, verify=False)
            except urllib3.exceptions.MaxRetryError as e:
                Utility.to_pickle(self._results, "OpenFIGI")
                print(str(e))
                response = 400
            if response.status_code != 200:
                self._results[work[0]] = f'Bad response code {str(response.status_code)}'
                self._queue.task_done()
            try:
                self._results[work[0]] = {"input": chunk, "output": response.json()}
            except decoder.JSONDecodeError as e:
                self._results[work[0]] = e.msg
                Utility.to_pickle(self._results, "OpenFIGI")
                self._queue.task_done()
            self._queue.task_done()
        return None

    def _populate_queue(self):
        """
        Populate the Queue to be used while retrieving data
        :return: a populated tuple representing the Queue of threads to execute
        """
        queue = Queue()
        if len(self._job_list) > 1:
            idx = list(range(0, len(self._job_list)))
            zipped_tuple = zip(idx, self._job_list)
            for i in zipped_tuple:
                queue.put(i)
        else:
            queue.put((0, self._job_list[0]))
        return queue

    def _run_multithreading(self):
        """Run the multi-threading construct"""
        num_threads = min(MULTITHREADING.get("num_threads"), len(self._job_list))
        for i in range(num_threads):
            print(f"Starting Thread {i}")
            worker = Thread(target=self._send_request)
            worker.daemon = True
            worker.start()
        self._queue.join()

    def _extended_results(self):
        """Build a instrument: result_of_query pairs for a more readable result"""
        results = list()
        identifiers = list()
        for idx in self._results:
            for key in self._results[idx]:
                if key == "input":
                    for identifier in self._results[idx][key]:
                        identifiers.append(identifier["idValue"])
                if key == "output":
                    for result in self._results[idx][key]:
                        if result.get("data"):
                            results.append(result.get("data")[0])
                        else:
                            results.append(result.get("error"))
        return dict(zip(identifiers, results))

    def to_df(self):
        """Transform the JSON response in a CSV"""
        index = list(self._results_extended.keys())
        columns = OPENFIGI.get("json_fields")
        data = list()
        for i in index:
            if type(self._results_extended[i]) != str:
                data.append(list(self._results_extended[i].values()))
            else:
                data.append([np.nan] * 12)
        return pd.DataFrame(data, index, columns)

    def get_id_value(self):
        """Return the idValues"""
        return self.id_id_value

    def get_results(self):
        """Return the results of the query"""
        return self._results

    def get_results_extended(self):
        """Return the extended results of the query"""
        return self._results_extended

    def get_results_to_df(self):
        """Return results in a DataFrame"""
        return self._to_df

    def get_results_to_excel(self, name="results.xlsx"):
        """
        Return results in a DataFrame
        :param str name: name of the file to save
        :return: a DataFrame with all the results
        :rtype: pd.DataFrame
        """
        return self._to_df.to_excel(name)
