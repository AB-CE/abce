# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
import zmq
import multiprocessing
import csv
import numpy as np


class AbceLogger(multiprocessing.Process):
    def __init__(self, directory, db_name, _addresses):
        multiprocessing.Process.__init__(self)
        self._addresses = _addresses
        self.file = open(directory + '/network.csv', 'wb')
        self.network_log = csv.writer(self.file, delimiter=',',
                            quotechar=",", quoting=csv.QUOTE_MINIMAL)

    def run(self):
        context = zmq.Context()
        in_sok = context.socket(zmq.PULL)
        in_sok.bind(self._addresses)
        while True:
            typ = in_sok.recv()
            if typ == "close":
                self.file.close()
                break
            if typ == 'network':
                data_to_write = in_sok.recv_pyobj()
                self.network_log.writerow(data_to_write)
        context.destroy()


