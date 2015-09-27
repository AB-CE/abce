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
import multiprocessing
import csv


class AbceLogger(multiprocessing.Process):
    def __init__(self, directory, in_sok):
        multiprocessing.Process.__init__(self)
        self.in_sok = in_sok
        self.directory = directory


    def run(self):
        csvfile = open(self.directory + '/network.csv', 'wb')
        network_log = csv.writer(csvfile, delimiter=',',
                            quotechar=",", quoting=csv.QUOTE_MINIMAL)
        while True:
            try:
                typ = self.in_sok.get()
            except KeyboardInterrupt:
                    csvfile.close()
                    break
            except EOFError:
                break
            if typ == "close":
                csvfile.close()
                break
            if typ == 'network':
                data_to_write = self.in_sok.get()
                network_log.writerow(data_to_write)


