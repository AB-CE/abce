import os
from os.path import join
import pandas as pd
import json
from flexx import ui
from .dockpanel import DockPanel
from .make_graphs import (make_panel_graphs,
                          make_simple_graphs,
                          make_aggregate_graphs,
                          make_histograms)
from .bokehwidget import BokehWidget
from abce.gui.webtext import abcedescription
from collections import defaultdict
import abce
from hashlib import sha1
from .loadform import LoadForm


def basiclayout(Form, simulation, title, top_bar=None, story={},
                texts=[abcedescription], pages=[], truncate_rounds=0,
                histograms=None):
    class Rex(ui.Widget):
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
                with DockPanel(flex=1) as self.dp:
                    self.form = Form(title='Simulation',
                                     style="location: N; overflow: scroll;")
                    self.loadform = LoadForm(
                                     title='Load',
                                     style="location: A; overflow-y: scroll;")
                    for i in range(len(texts)):
                        ui.Label(title=texts[i].splitlines()[0],
                                 text='\n'.join(texts[i].splitlines()[1:]),
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

            @self.form.connect("run_simulation")
            def run_simulation(events):

                self.progress_label.title = 'Running...'
                self.progress_label.text = 'Simulation in progress'

                simulation(events['simulation_parameter'])

                self.progress_label.title = 'Success'

                self.display_results(events)
                self.progress_label.text = (
                    'Simulation succeeded, generating graphs')

                self.progress_label.title = 'Results:'
                self.progress_label.text = 'Click left'

            @self.form.connect("repeatexecution")
            def _repeatexecution(events):
                name, parameters = hash_simulation_parameters(events)
                parameters['Name'] = name
                pool_path = join(os.path.abspath('./result/cache'), name)

                if name not in self.graphs:
                    self.graphs[name] = load_cached(pool_path, name)

                self.print_continuously_updating()
                abce.simulation_name = name
                switch_on_conditional_logging(parameters, histograms)
                simulation(parameters)
                del abce.simulation_name
                del abce.conditional_logging
                path = newest_subdirectory('./result', name)
                for filename in os.listdir(path):
                    if (filename is not 'trade.csv' and
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
            def display_results(events):
                self.display_results(events)

            @self.form.connect('update_parameter_database')
            def _update_parameter_database(events):
                self.loadform.update(events)

            @self.loadform.connect("load")
            def _load(event):
                self.form.load_parameter(event)
                self.dp.selectWidget(self.form)

        def display_results(self, events):
            if self.first:
                self.plot_widgets = []
            try:
                ignore_initial_rounds = int(events['ignore_initial_rounds'])
            except KeyError:
                ignore_initial_rounds = 100

            try:
                path = events['subdir']
            except KeyError:
                path = newest_subdirectory('./result')

            i = 0
            for filename in os.listdir(path):
                if not filename.endswith('.csv'):
                    continue

                df = pd.read_csv(path + filename).ix[truncate_rounds:]
                try:
                    rounds = max(df['round'])
                except KeyError:
                    rounds = max(df['index'])
                if ignore_initial_rounds >= rounds:
                    ignore_initial_rounds = 0
                    print('abcegui.py ignore_initial_rounds >= rounds')
                if (filename.startswith('aggregate_') or
                        filename.startswith('aggregated_')):
                    titles, plots = make_aggregate_graphs(
                        df, filename, ignore_initial_rounds)
                else:
                    try:
                        if max(df.get('id', [0])) == 0:
                            titles, plots = make_simple_graphs(
                                df, filename, ignore_initial_rounds)
                        else:
                            titles, plots = make_panel_graphs(
                                df, filename, ignore_initial_rounds)
                    except ValueError as e:
                        print(filename, 'not displayable: ValueError', e)

                if self.first:
                    with self.dp:
                        for plottitle, plot in zip(titles, plots):
                            pw = BokehWidget(plot=plot,
                                             style="location: A",
                                             title=plottitle)
                            self.plot_widgets.append(pw)
                        self.dp.selectWidget(self.plot_widgets[0])
                else:
                    for plot in plots:
                        self.plot_widgets[i].plot = plot
                        i += 1

            self.first = False

        def display_repeat_execution(self, graphs):
            if self.first_repeat:
                self.repeat_plot_widgets = []
            i = 0
            for filename, data in graphs.items():
                titles, plots = make_histograms(data, filename, 0)

                if self.first_repeat:
                    with self.dp:
                        for plottitle, plot in zip(titles, plots):
                            pw = BokehWidget(plot=plot,
                                             style="location: A",
                                             title=plottitle)
                            self.repeat_plot_widgets.append(pw)
                        self.dp.selectWidget(self.repeat_plot_widgets[0])
                else:
                    for plot in plots:
                        self.repeat_plot_widgets[i].plot = plot
                        i += 1
            self.first_repeat = False

        def print_continuously_updating(self):
            self.progress_label.title = 'Continuously updating'
            self.progress_label.text = 'Series of simulations in progress'

    return Rex


def newest_subdirectory(directory='.', name=''):
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
    parameters = events['simulation_parameter']
    parameters['random_seed'] = None
    parameters['Name'] = ''
    name = sha1(json.dumps(parameters, sort_keys=True)
                .encode('utf-8')).hexdigest()
    return name, parameters


def load_cached(pool_path, name):
    """ Loads a file and creates directory if file does not exist    """
    graphs = defaultdict(pd.DataFrame)
    try:
        for filename in os.listdir(pool_path):
            graphs[filename] = pd.read_pickle(join(pool_path, filename))
    except FileNotFoundError:
        os.makedirs(pool_path)
    return graphs


def switch_on_conditional_logging(parameters, histograms):
    if histograms is not None:
        abce.conditional_logging = histograms
    elif 'rounds' in parameters:
        abce.conditional_logging = [parameters['rounds'] - 1]
    elif 'histogram' in parameters:
        abce.conditional_logging = [parameters['histogram']]
    else:
        raise Exception("In @gui specify when histograms should be produced")
