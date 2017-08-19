import os
import pandas as pd
from flexx import ui
from .dockpanel import DockPanel
from .make_graphs import (make_panel_graphs,
                          make_simple_graphs,
                          make_aggregate_graphs)
from .bokehwidget import BokehWidget
from abce.gui.webtext import abcedescription
from collections import defaultdict


def basiclayout(Form, simulation, title, top_bar=None, story={},
                texts=[abcedescription], pages=[], truncate_rounds=0):
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
            self.graphs = defaultdict(pd.DataFrame)
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
                    for i in range(len(texts)):
                        ui.Label(title=texts[i].splitlines()[0],
                                 text='\n'.join(texts[i].splitlines()[1:]),
                                 style="location: R; overflow: scroll;",
                                 wrap=True)
                    for pagetitle, page in pages:
                        ui.IFrame(url=page,
                                  title=pagetitle,
                                  style="location: A; overflow: scroll;",)
                    self.progress_label = ui.Label(title=' ',
                        text='Click tab, move tabs by dragging tabs, resize windows',
                        style="location: S; overflow: scroll;",
                        wrap=True)

            @self.form.connect("run_simulation")
            def run_simulation(events):

                self.progress_label.title = 'Running...'
                self.progress_label.text = 'Simulation in progress'

                simulation(events['simulation_parameter'])

                self.progress_label.title = 'Success'

                self.display_results(events)
                self.progress_label.text = 'Simulation succeeded, generating graphs'

                self.progress_label.title = 'Results:'
                self.progress_label.text = 'Click left'

            @self.form.connect("repeatexecution")
            def _repeatexecution(events):
                print('xx')
                parameters = events['simulation_parameter']
                parameters['random_seed'] = None
                parameters['name'] = 'repeatexecution'
                simulation(parameters)
                path = newest_subdirectory('./result')
                for filename in os.listdir(path):
                    if filename.startswith('aggregate_'):
                        final_values = pd.read_csv(path + filename).iloc[-1:]
                        print('*****')
                        print(final_values)
                        print('*****')
                        self.graphs[filename[10:]] = self.graphs[filename[10:]].append(final_values).reset_index(drop=True)
                self.display_repeat_execution(self.graphs)
                self.form.repeat_execution()

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
                if filename.startswith('aggregate_'):
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
                    except ValueError:
                        print((filename, 'not displayable: ValueError'))

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
            for fn, g in graphs.items():
                print(g)

                titles, plots = make_simple_graphs(g, fn, 0, index=True)

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

    return Rex


def newest_subdirectory(directory='.'):
    directory = os.path.abspath(directory)
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]
    return max(all_subdirs, key=os.path.getmtime) + '/'
