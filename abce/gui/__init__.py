import os
import abce
import dataset
from flexx import app, ui, event
from .basiclayout import basiclayout
from .form import form
from abce.gui.webtext import abcedescription
import flexx


def gui(parameter_mask={}, names={}, top_bar=None, story={},
        title="Agent-Based Computational Economics",
        serve=False, runtime='browser-X', truncate_rounds=0,
        texts=[abcedescription], pages=[], histograms=None):
    """ gui is a decorator that can be used to add a graphical user interface
    to your simulation.

    Args:

        parameter_mask:
            a dictionary with the parameter name as key and an example value
            as value. Instead of the example value you can also put a tuple:
            (min, default, max)

            parameters can be:
                - float:
                    {'exponent': (0.0, 0.5, 1.1)}

                - int:
                    {'num_firms': (0, 100, 100000)}

                - dict or list, which should be strings of a dict or a
                  list (see example):
                    {'list_to_edit': "['brd', 'mlk', 'add']"}

                - a list of options:
                    {'several_options': ['opt_1', 'opt_2', 'opt_3']}

                - a string:
                    {'name': '2x2'}

        names (optional):
            a dictionary with the parameter name as key and an alternative
            text to be displayed instead.

        title:
            a string with the name of the simulation.

        top_bar:
            html string for a bar on the top

        story:
            a dictionary with text to be displayed alongeside the graphs.
            Key must be the graphs title, value can be text or html.


        serve:
            If you run this on your local machine serve must be False.
            If used with an uWSGI/Nginx or different web server must be True

        truncate_rounds:
            Does not display the initial x rounds

        runtime:
            webbrowser to start the simulation in, can be 'xui' or python's
            webbrowser module's webrowser string.

        histograms:
            specifies in which round histograms are generated. If it is
            not specified rounds from the menu is used. If this is not
            specified, make 'histogram' slider.

    Example::

        parameter_mask = {'name': 'name',
                             'trade_logging': 'off',
                             'random_seed': None,
                             'num_rounds': 40,
                             'num_firms': (0, 100, 100000),
                             'num_household': (0, 100, 100000),
                             'exponent': (0.0, 0.5, 1.1),
                             'several_options': ['opt_1', 'opt_2', 'opt_3']
                             'list_to_edit': "['brd', 'mlk', 'add']",
                             'dictionary_to_edit': "{'v1': 1, 'v2': 2}"}

        names = {'num_firms': 'Number of Firms'}

        @gui(parameter_mask, names,
             title="Agent-Based Computational Economics",
             top_bar=None, story={}, serve=False)
        def main(simulation_parameters):
            simulation = Simulation(simulation_parameters)
            firms = simulation.build_agents(Firm,
                simulation_parameters['num_firms'])
            households = simulation.build_agents(Household,
                simulation_parameters['num_households'])

            for r in range(199):
                simulation.advance_round(r)
                firms.work()
                households.buy()

        if __name__ == '__main__':
            main(simulation_parameters)
    """
    if any('SPYDER' in name for name in os.environ):
        title = """WARNING: You are running this Simulation in SPYDER
                 When you run an IDE such as spyder the website
                 blocks. In order to avoid that, modify the 'Run Setting'
                 and choose 'Execute in external System Terminal' and
                 restart your system """
        print(title)

    def inner(simulation):
        database = dataset.connect('sqlite:///parameter.db')
        abce.parameter_database = database['parameter']
        Form = form(parameter_mask, names)
        if serve:
            flexx.config.hostname = '0.0.0.0'
            flexx.config.port = 80
            app.serve(basiclayout(Form, simulation, title, top_bar,
                                  truncate_rounds,
                                  texts=texts, pages=pages,
                                  histograms=histograms))
            app.start()
        else:
            app.launch(basiclayout(Form, simulation, title, top_bar,
                                   truncate_rounds,
                                   texts=texts, pages=pages,
                                   histograms=histograms),
                       windowmode='maximized', runtime=runtime)
            app.run()
        return lambda _: None
    return inner


def display_graphs(parameter):
    text = ""
    for key, value in parameter.items():
        text = "%s%s: %s<br>" % (text, key, str(value))

    class Form(ui.Widget):
        def init(self):
            ui.Label(text=text)
            self.btn = ui.Button(text="display")

        @event.connect('btn.mouse_click')
        def wdg(self, *event):
            print('__init__')
            self.emit('display_results', {})

    app.launch(basiclayout(Form, None, parameter['name'], None, 0),
               runtime='browser-X')
    app.run()
