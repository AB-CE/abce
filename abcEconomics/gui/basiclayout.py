""" A graphical user interface for abcEconomics simulations """
import os
from os.path import join
import json
from hashlib import sha1
from collections import defaultdict
from flexx import ui
import abcEconomics
from .dockpanel import DockPanel
from .make_graphs import (make_panel_graphs,
                          make_simple_graphs,
                          make_aggregate_graphs)
from .bokehwidget import BokehWidget
from .webtext import abcEconomicsdescription
from .loadform import LoadForm
try:
    import pandas as pd
except ImportError:
    pass


css_style = 'background-color: steelblue;'


def basiclayout(Form, simulation, title, top_bar=None, story=None,
                texts=None, pages=None, truncate_rounds=0,
                histograms=None, graphs=False):
    """ Generates the basic layout of the website  """
    story = ({} if story is None else story)
    pages = ({} if pages is None else pages)
    texts = ([abcEconomicsdescription] if texts is None else texts)

    class abcEconomics(ui.Widget):
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
            self.first = True
            self.graphs = {}
            with ui.BoxLayout(orientation='v',
                              style=css_style):
                with ui.HBox(flex=0):
                    ui.Label(text='<h1 style="color: white">%s</h1>' % title,
                             flex=1,
                             style=css_style)
                if top_bar is not None:
                    ui.Label(text=top_bar,
                             flex=0,
                             style=css_style)
                with DockPanel(flex=1) as self.dockpanel:
                    if not graphs:
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

            else:
                @self.form.connect("run_simulation")
                def run_simulation(events):
                    """ Runs simulation and shows results """
                    self.display_status('Running...', 'Simulation in progress')
                    abcEconomics.simulation_name, parameters = (
                        hash_simulation_parameters(events))
                    simulation(parameters)
                    self.display_status('Success',
                                        'Simulation succeeded, generating graphs')
                    self.display_results(events, abcEconomics.simulation_name)
                    self.display_status('Results:', 'Click left')
                    del abcEconomics.simulation_name

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
                    print('abcEconomicsgui.py ignore_initial_rounds >= rounds')
                if (filename.startswith('aggregate_') or
                        filename.startswith('aggregated_')):
                    titles, plots = make_aggregate_graphs(
                        table, filename, ignore_initial_rounds)
                else:
                    try:
                        try:
                            titles, plots = make_panel_graphs(table, filename, ignore_initial_rounds)
                        except KeyError as error:
                            raise error
                            titles, plots = make_simple_graphs(
                                table, filename, ignore_initial_rounds)
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

    return abcEconomics


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
    """ Uses abcEconomics.conditional_logging, to instruct the simulation, to log
    only at a specific point of time """
    if histograms is not None:
        abcEconomics.conditional_logging = histograms
    elif 'rounds' in parameters:
        abcEconomics.conditional_logging = [parameters['rounds'] - 1]
    elif 'histogram' in parameters:
        abcEconomics.conditional_logging = [parameters['histogram']]
    else:
        raise Exception("In @gui specify when histograms should be produced")
