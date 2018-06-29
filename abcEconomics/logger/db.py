# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you
# are requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import datetime
import json
import os
import threading
import multiprocessing
import time
from collections import defaultdict

import dataset

from .online_variance import OnlineVariance
from .postprocess import to_csv
import queue


class DbDatabase:
    """Separate thread that receives data from in_sok and saves it into a
    database"""

    def __init__(self, directory, name, in_sok, trade_log, plugin=None, pluginargs=[]):
        super().__init__()

        # setting up directory
        self.directory = directory
        if directory is not None:
            os.makedirs(os.path.abspath('.') + '/result/', exist_ok=True)
            if directory == 'auto':
                self.directory = (os.path.abspath('.') + '/result/' + name + '_' +
                             datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
                """ the directory variable contains the directory of the simulation outcomes
                it can be used to generate your own graphs as all resulting
                csv files are there.
                """
            else:
                self.directory = directory
            while True:
                try:
                    os.makedirs(self.directory)
                    break
                except OSError:
                    self.directory += 'I'

        self.panels = {}
        self.in_sok = in_sok
        self.data = {}
        self.trade_log = trade_log

        self.aggregation = defaultdict(lambda: defaultdict(OnlineVariance))
        self.round = 0

        self.plugin = plugin
        self.pluginargs = pluginargs

    def run(self):
        if self.plugin is not None:
            self.plugin = self.plugin(*self.pluginargs)
        self.dataset_db = dataset.connect('sqlite://')
        self.dataset_db.query('PRAGMA synchronous=OFF')
        # self.dataset_db.query('PRAGMA journal_mode=OFF')
        self.dataset_db.query('PRAGMA count_changes=OFF')
        self.dataset_db.query('PRAGMA temp_store=OFF')
        self.dataset_db.query('PRAGMA default_temp_store=OFF')
        table_log = {}
        current_log = defaultdict(list)
        current_trade = []
        self.table_aggregates = {}

        if self.trade_log:
            trade_table = self.dataset_db.create_table('trade___trade',
                                                       primary_id='index')

        while True:
            try:
                msg = self.in_sok.get(timeout=120)
            except queue.Empty:
                print("simulation.finalize() must be specified at the end of simulation")
                msg = self.in_sok.get()

            if msg[0] == 'snapshot_agg':
                _, round, group, data_to_write = msg
                if self.round == round:
                    for key, value in data_to_write.items():
                        self.aggregation[group][key].update(value)
                else:
                    self.make_aggregation_and_write()
                    self.round = round
                    for key, value in data_to_write.items():
                        self.aggregation[group][key].update(value)

            elif msg[0] == 'trade_log':
                for (good, seller, buyer, price), quantity in msg[1].items():
                    current_trade.append({'round': msg[2],
                                          'good': good,
                                          'seller': seller,
                                          'buyer': buyer,
                                          'price': price,
                                          'quantity': quantity})
                    if len(current_trade) == 1000:
                        trade_table.insert_many(current_trade)
                        current_trade = []

            elif msg[0] == 'log':
                _, group, name, round, data_to_write, subround_or_serial = msg
                table_name = 'panel___%s___%s' % (group, subround_or_serial)
                data_to_write['round'] = str(round)
                data_to_write['name'] = str(name)
                current_log[table_name].append(data_to_write)
                if len(current_log[table_name]) == 1000:
                    if table_name not in table_log:
                        table_log[table_name] = self.dataset_db.create_table(
                            table_name, primary_id='index')
                    table_log[table_name].insert_many(current_log[table_name])
                    current_log[table_name] = []

            elif msg == "close":
                break

            else:
                try:
                    getattr(self.plugin, msg[0])(*msg[1], **msg[2])
                except AttributeError:
                    raise AttributeError(
                        "abcEconomics_db error '%s' command unknown" % msg)

        for name, data in current_log.items():
            if name not in self.dataset_db:
                table_log[name] = self.dataset_db.create_table(
                    name, primary_id='index')
            table_log[name].insert_many(data)
        self.make_aggregation_and_write()
        if self.trade_log:
            trade_table.insert_many(current_trade)
        self.dataset_db.commit()
        try:
            self.plugin.close()
        except AttributeError:
            pass
        if self.directory is not None:
            to_csv(self.directory, self.dataset_db)

    def make_aggregation_and_write(self):
        for group, table in self.aggregation.items():
            result = {'round': self.round}
            for key, data in table.items():
                result[key + '_ttl'] = data.sum()
                result[key + '_mean'] = data.mean()
                result[key + '_std'] = data.std()
            try:
                self.table_aggregates[group].insert(result)
            except KeyError:
                self.table_aggregates[group] = self.dataset_db.create_table(
                    'aggregate___%s' % group, primary_id='index')
                self.table_aggregates[group].insert(result)
            self.aggregation[group].clear()

    def finalize(self, data):
        self.in_sok.put('close')
        while self.is_alive():
            time.sleep(0.05)
        self._write_description_file(data)

    def _write_description_file(self, data):
        if self.directory is not None:
            with open(os.path.abspath(self.directory + '/description.txt'), 'w') as description:
                description.write(json.dumps(
                    data,
                    indent=4,
                    skipkeys=True,
                    default=lambda x: 'not_serializeable'))


class ThreadingDatabase(DbDatabase, threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MultiprocessingDatabase(DbDatabase, multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
