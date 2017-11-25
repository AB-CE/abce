""" A graphical user interface for ABCE simulations """
import os
from os.path import join
import json
from hashlib import sha1
from collections import defaultdict
import pandas as pd
from flexx import ui
import abce
from .dockpanel import DockPanel
from .make_graphs import (make_panel_graphs,
                          make_simple_graphs,
                          make_aggregate_graphs,
                          make_histograms)
from .bokehwidget import BokehWidget
from .webtext import abcedescription
from .loadform import LoadForm


def basiclayout(Form, simulation, title, top_bar=None, story=None,
                texts=None, pages=None, truncate_rounds=0,
                histograms=None, graphs=False):
    """ Generates the basic layout of the website  """
    story = ({} if story is None else story)
    pages = ({} if pages is None else pages)
    texts = ([abcedescription] if texts is None else texts)

    class ABCE(ui.Widget):
        """ Basic layout of the website  """
        CSS = """
        h1, a {
            -webkit-margin-before: 0.20em;
            -webkit-margin-after: 0.0em;
            -webkit-margin-start: 1em;
            -webkit-margin-end: 1em;
            text-decoration: none;
        }
        ::-webkit-scrollbar {
          -webkit-appearance: none;
          width: 10px;
        }

        ::-webkit-scrollbar-thumb {
          border-radius: 5px;
          background-color: rgba(0,0,0,.5);
          -webkit-box-shadow: 0 0 1px rgba(255,255,255,.5);
        }

         """

        def init(self):
            self.graphs = {}
            self.first = self.first_repeat = True
            with ui.BoxLayout(orientation='v',
                              style="background-color: blue;"):
                with ui.HBox(flex=0):
                    ui.Label(text='<h1 style="color: white">%s</h1>' % title,
                             flex=1,
                             style="background-color: blue;")
                if top_bar is not None:
                    ui.Label(text=top_bar,
                             flex=0,
                             style="background-color: blue;")
                with DockPanel(flex=1) as self.dockpanel:
                    self.form = Form(title='Simulation',
                                     style="location: N; overflow: scroll;")
                    self.loadform = LoadForm(
                        title='Load',
                        style="location: A; overflow-y: scroll;")
                    for text in texts:
                        ui.Label(title=text.splitlines()[0],
                                 text='\n'.join(text.splitlines()[1:]),
                                 style="location: R; overflow: scroll;",
                                 wrap=True)
                    for pagetitle, page in pages:
                        ui.IFrame(url=page,
                                  title=pagetitle,
                                  style="location: A; overflow: scroll;")
                    self.progress_label = ui.Label(
                        title=' ',
                        text='Move tabs by dragging tabs; resize windows',
                        style="location: S; overflow: scroll;",
                        wrap=True)

            if graphs:
                self.display_results({'simulation_name': ''}, '')

            @self.form.connect("run_simulation")
            def run_simulation(events):
                """ Runs simulation and shows results """
                self.display_status('Running...', 'Simulation in progress')
                abce.simulation_name, parameters = (
                    hash_simulation_parameters(events))
                simulation(parameters)
                self.display_status('Success',
                                    'Simulation succeeded, generating graphs')
                self.display_results(events, abce.simulation_name)
                self.display_status('Results:', 'Click left')
                del abce.simulation_name

            @self.form.connect("repeatexecution")
            def _repeatexecution(events):
                name, parameters = hash_simulation_parameters(events)
                print("parameters:", parameters)
                parameters['Name'] = name
                pool_path = join(os.path.abspath('./result/cache'), name)

                if name not in self.graphs:
                    self.graphs[name] = load_cached(pool_path)

                self.display_status('Continuously updating',
                                    'Series of simulations in progress')
                abce.simulation_name = name
                switch_on_conditional_logging(parameters, histograms)
                simulation(parameters)
                del abce.simulation_name
                del abce.conditional_logging
                path = newest_subdirectory('./result', name)
                for filename in os.listdir(path):
                    if (filename != 'trade.csv' and
                            filename.endswith('.csv')):
                        self.graphs[name][filename] = (
                            self.graphs[name][filename]
                            .append(pd.read_csv(join(path, filename)))
                            .reset_index(drop=True))
                        if len(self.graphs[name][filename]) % 10 == 0:
                            self.graphs[name][filename].to_pickle(
                                join(pool_path, filename))
                number_obs = len(list(self.graphs[name].values())[0])
                if number_obs < 12 or number_obs % 10 == 0:
                    self.display_repeat_execution(self.graphs[name])
                self.form.emit('_repeat_execution', events)

            @self.form.connect('display_results')
            def display_results(events):  # pylint: disable=W0612
                """ Forwarder """
                self.display_results(events, events['simulation_name'])

            @self.form.connect('update_parameter_database')
            def _update_parameter_database(events):
                """ Forwarder """
                self.loadform.update(events)

            @self.loadform.connect("load")
            def _load(event):
                self.form.load_parameter(event)
                self.dockpanel.selectWidget(self.form)

        def display_status(self, title, text):
            """ displays status on bottom left
            as first tab of results panel """
            self.progress_label.title = title
            self.progress_label.text = text

        def display_results(self, events, simulation_name):  # pylint: disable=R0912
            """ Displays results of single simulation_name """
            if self.first:
                self.plot_widgets = []
            try:
                ignore_initial_rounds = int(events['ignore_initial_rounds'])
            except KeyError:
                ignore_initial_rounds = 100

            try:
                path = events['subdir']
            except KeyError:
                path = newest_subdirectory('./result', simulation_name)

            i = 0
            for filename in os.listdir(path):
                if not filename.endswith('.csv'):
                    continue

                table = pd.read_csv(path + filename).ix[truncate_rounds:]
                try:
                    rounds = max(table['round'])
                except KeyError:
                    rounds = max(table['index'])
                if ignore_initial_rounds >= rounds:
                    ignore_initial_rounds = 0
                    print('abcegui.py ignore_initial_rounds >= rounds')
                if (filename.startswith('aggregate_') or
                        filename.startswith('aggregated_')):
                    titles, plots = make_aggregate_graphs(
                        table, filename, ignore_initial_rounds)
                else:
                    try:
                        if max(table.get('id', [0])) == 0:
                            titles, plots = make_simple_graphs(
                                table, filename, ignore_initial_rounds)
                        else:
                            titles, plots = make_panel_graphs(table, filename, ignore_initial_rounds)
                    except ValueError as error:
                        print(filename, 'not displayable: ValueError', error)

                if self.first:
                    with self.dockpanel:
                        for plottitle, plot in zip(titles, plots):
                            plotwidget = BokehWidget(plot=plot,
                                                     style="location: A",
                                                     title=plottitle)
                            self.plot_widgets.append(plotwidget)
                        self.dockpanel.selectWidget(self.plot_widgets[0])
                else:
                    for plot in plots:
                        self.plot_widgets[i].plot = plot
                        i += 1

            self.first = False

        def display_repeat_execution(self, graphs):
            """ Displays histograms of repeat executions """
            if self.first_repeat:
                self.repeat_plot_widgets = []
            i = 0
            for filename, data in graphs.items():
                titles, plots = make_histograms(data, filename)

                if self.first_repeat:
                    with self.dockpanel:
                        for plottitle, plot in zip(titles, plots):
                            plotwidget = BokehWidget(plot=plot,
                                                     style="location: A",
                                                     title=plottitle)
                            self.repeat_plot_widgets.append(plotwidget)
                        self.dockpanel.selectWidget(
                            self.repeat_plot_widgets[0])
                else:
                    for plot in plots:
                        self.repeat_plot_widgets[i].plot = plot
                        i += 1
            self.first_repeat = False
    return ABCE


def newest_subdirectory(directory='.', name=''):
    """ Returns the newes subdirectory in the 'directory/name' directory """
    directory = os.path.abspath(directory)
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]
    all_subdirs = sorted(all_subdirs, key=os.path.getmtime, reverse=True)
    for subdir in all_subdirs:
        if name in subdir:
            return subdir + '/'
    raise Exception()


def hash_simulation_parameters(events):
    """ hashes simulation parameter, after setting random seed to None """
    parameters = events['simulation_parameter']
    parameters['random_seed'] = None
    parameters['name'] = None
    parameters['Name'] = None
    name = sha1(json.dumps(parameters, sort_keys=True)
                .encode('utf-8')).hexdigest()
    return name, parameters


def load_cached(pool_path):
    """ Loads a file and creates directory if file does not exist    """
    graphs = defaultdict(pd.DataFrame)
    try:
        for filename in os.listdir(pool_path):
            graphs[filename] = pd.read_pickle(join(pool_path, filename))
    except FileNotFoundError:
        os.makedirs(pool_path)
    return graphs


def switch_on_conditional_logging(parameters, histograms):
    """ Uses abce.conditional_logging, to instruct the simulation, to log
    only at a specific point of time """
    if histograms is not None:
        abce.conditional_logging = histograms
    elif 'rounds' in parameters:
        abce.conditional_logging = [parameters['rounds'] - 1]
    elif 'histogram' in parameters:
        abce.conditional_logging = [parameters['histogram']]
    else:
        raise Exception("In @gui specify when histograms should be produced")
