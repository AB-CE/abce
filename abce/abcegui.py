from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Markup
import webbrowser
import os
import pandas as pd
from abce.webtext import abcedescription
import shutil
import traceback
import random
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import Range1d, LinearAxis
from bokeh.io import gridplot
import json
import datetime
import time
from abcegui_helper import find_free_port, load_text

colors = ["red","blue","green","black","purple","pink",
          "yellow","orange","pink","Brown","Cyan","Crimson",
          "DarkOrange","DarkSeaGreen","DarkCyan","DarkBlue","DarkViolet","Silver",
          "#0FCFC0","#9CDED6","#D5EAE7","#F3E1EB","#F6C4E1","#F79CD4"]

_ = __file__  # makes sure that the templates can be reached

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

inputs = []
simulation = None
gtitle = 'ABCE Simulation'
gtext = abcedescription
opened = False

def gui(parameters, names=None, title=None, text=None, self_hosted=True):
    """ gui is a decorator that can be used to add a graphical user interface
    to your simulation.

    Args:

        parameters:
            a dictionary with the parameter name as key and an example value as
            value. Instead of the example value you can also put a tuple:
            (min, default, max)

            parameters can be:
                - float:
                    {'exponent': (0.0, 0.5, 1.1)}

                - int:
                    {'num_firms': (0, 100, 100000)}

                - dict or list, which should be strings of a dict or a list (see example):
                    {'list_to_edit': "['brd', 'mlk', 'add']"}

                - everything else that can be evaluated as a string, see
                  (eval)[https://docs.python.org/2/library/functions.html#eval]

                - a list of options:
                    {'several_options': ['opt_1', 'opt_2', 'opt_3']}

                - a string:
                    {'name': '2x2'}

        names (optional):
            a dictionary with the parameter name as key and an alternative
            text to be displayed instead.

        title:
            a string with the name of the simulation.

        text:
            a description text of the simulation. Can be html.

        self_hosted:
            If you run this on your local machine self_hosted must be True.
            If used with an uWSGI/Nginx or different web server must be False


    Example::

        simulation_parameters = {'name': 'name',
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

        @gui(parameters, simulation_parameters, names=names)
        def main(simulation_parameters):
            w = Simulation(simulation_parameters)
            action_list = [
            ('household', 'sell_labor'),
            ('firm', 'buy_inputs'),
            ('firm', 'production')]
            w.add_action_list(action_list)

            w.build_agents(Firm, simulation_parameters['num_firms'])
            w.build_agents(Household, simulation_parameters['num_households'])
            w.run()

        if __name__ == '__main__':
            main(simulation_parameters)
    """
    if any('SPYDER' in name for name in os.environ):
        title = "WARNING"
        text = """WARNING: You are running this Simulation in SPYDER
                 When you run an IDE such as spyder the website
                 blocks. In order to avoid that, modify the 'Run Setting'
                 and choose 'Execute in external System Terminal' and
                 restart your system """
        print(text)
    def inner(func):
        generate(new_inputs=parameters, new_simulation=func, names=names, title=title, text=text)
        if self_hosted:
            return run
        else:
            return lambda open, new: pass
    return inner  # return a function object

def newest_subdirectory(directory='.'):
    directory = os.path.abspath(directory)
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]
    return  max(all_subdirs, key=os.path.getmtime) + '/'

@app.route('/')
def show_entries():
    return render_template('show_entries.html', entries=inputs, title=gtitle, text=gtext)

@app.route('/submitted_simulation', methods=['POST'])
def submitted_simulation():
    parameters = {}
    form = request.form.to_dict()
    for element in inputs:
        name = element['name']
        if element['type'] == bool:
            parameters[name] = name in form
        elif element['type'] == str:
            try:
                parameters[name] = eval(form[name])
            except:
                parameters[name] = form[name].replace('\n','').replace('\r', '').lstrip().rstrip()
        else:
            parameters[name] = element['type'](form[name])
    simulation(parameters)
    return redirect(url_for('show_simulation'))

def make_title(title, col):
    return title.replace('aggregate_', '').replace('panel_', '').replace('.csv', '')  + ' ' + col


def make_aggregate_graphs(df, filename, ignore_initial_rounds):
    print 'make_aggregate_graphs', filename
    columns = [col for col in df.columns if not col.endswith('_std')
                                         and not col.endswith('_mean')
                                         and not col in ['index', 'round', 'id', 'date']]
    plots = {}
    try:
        index = df['date'].apply(lambda sdate: datetime.date(*[int(c) for c in sdate.split('-')]))
        x_axis_type="datetime"
    except KeyError:
        index = df['round']
        x_axis_type="linear"
    for col in columns:
        title = make_title(filename, col)
        plot = figure(title=title, responsive=True, webgl=False, x_axis_type=x_axis_type,
                      tools="pan, wheel_zoom, box_zoom, save, crosshair, hover")
        plot.yaxis.visible = None
        plot.legend.orientation = "top_left"
        if df[col].min(skipna=True) != df[col].max(skipna=True):
            plot.extra_y_ranges['ttl'] = Range1d(df[col].min(skipna=True), df[col].ix[ignore_initial_rounds:].max(skipna=True))
        else:
            plot.extra_y_ranges['ttl'] = Range1d(df[col].min(skipna=True) - 1, df[col].ix[ignore_initial_rounds:].max(skipna=True) + 1)

        plot.line(index, df[col],
                  legend='mean/total', line_width=2, line_color='blue', y_range_name="ttl")
        plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')

        try:
            if df[col].min() != df[col].max():
                plot.extra_y_ranges['std'] = Range1d(df[col + '_std'].min(skipna=True), df[col + '_std'].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['std'] = Range1d(df[col + '_std'].min(skipna=True) - 1, df[col + '_std'].ix[ignore_initial_rounds:].max(skipna=True) + 1)
            plot.line(index, df[col + '_std'],
                      legend='std', line_width=2, line_color='red', y_range_name="std")
            plot.add_layout(LinearAxis(y_range_name="std"), 'right')
        except KeyError:
            pass
        try:
            if df[col].min() != df[col].max():
                plot.extra_y_ranges['mean'] = Range1d(df[col + '_mean'].min(skipna=True), df[col + '_mean'].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['mean'] = Range1d(df[col + '_mean'].min(skipna=True) - 1 , df[col + '_mean'].ix[ignore_initial_rounds:].max(skipna=True) + 1)
            #plot.line(index), df[col],
            #          legend='mean', line_width=2, line_color='green', y_range_name="mean")
            plot.add_layout(LinearAxis(y_range_name="mean"), 'left')
        except KeyError:
            pass
        plots[json.dumps((plot.ref['id'], title + ' (agg)'))] = plot
    return plots

def make_simple_graphs(df, filename, ignore_initial_rounds):
    print 'make_simple_graphs', filename
    plots = {}
    try:
        index = df['date'].apply(lambda sdate: datetime.date(*[int(c) for c in sdate.split('-')]))
        x_axis_type="datetime"
    except KeyError:
        index = df['round']
        x_axis_type="linear"
    for col in df.columns:
        if col not in ['round', 'id', 'index', 'date']:
            title = make_title(filename, col)
            plot = figure(title=title, responsive=True, webgl=False, x_axis_type=x_axis_type,
                      tools="pan, wheel_zoom, box_zoom, save, crosshair, hover")
            plot.yaxis.visible = None
            plot.legend.orientation = "top_left"
            if df[col].min(skipna=True) != df[col].max(skipna=True):
                plot.extra_y_ranges['ttl'] = Range1d(df[col].min(skipna=True), df[col].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['ttl'] = Range1d(df[col].min(skipna=True) - 1, df[col].ix[ignore_initial_rounds:].max(skipna=True) + 1)

            plot.legend.orientation = "top_left"
            plot.line(index, df[col], legend=col, line_width=2, line_color='blue', y_range_name="ttl")
            plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')

            plots[json.dumps((plot.ref['id'], title))] = plot
    return plots

def make_panel_graphs(df, filename, ignore_initial_rounds):
    print 'make_panel_graphs', filename
    if 'date' in df.columns:
        x_axis_type="datetime"
    else:
        x_axis_type="linear"


    if  max(df['id'])> 20:
        individuals = sorted(random.sample(range(max(df['id'])), 20))
    else:
        individuals = range(max(df['id']) + 1)
    df = df[df['id'].isin(individuals)]
    plots = {}
    for col in df.columns:
        if col not in ['round', 'id', 'index', 'date']:
            title = make_title(filename, col)
            plot = figure(title=title, responsive=True, webgl=False, x_axis_type=x_axis_type,
                      tools="pan, wheel_zoom, box_zoom, save, crosshair, hover")

            plot.legend.orientation = "top_left"
            for i, id in enumerate(individuals):
                try:
                    index = df['date'][df['id'] == id].apply(lambda sdate: datetime.date(*[int(c) for c in sdate.split('-')]))
                except KeyError:
                    index = df['round'][df['id'] == id]
                series = df[col][df['id'] == id]
                plot.line(index, series, legend=str(id), line_width=2, line_color=colors[i])
            plots[json.dumps((plot.ref['id'], title + '(panel)'))] = plot
    return plots

@app.route('/show_simulation')
def show_simulation():
    rounds = 0
    ignore_initial_rounds = int(session.get('ignore_initial_rounds', 0))
    plots = {}
    filenames = []
    path = request.args.get('subdir')
    if path is None:
        path = newest_subdirectory('./result')
    try:
        with open(path + 'description.txt') as desc_file:
            desc = desc_file.read()
    except IOError:
        desc = ''

    plots = {}

    for filename in os.listdir(path):
        if not filename.endswith('.csv'):
            continue
        elif filename.startswith('#'):
            continue
        df = pd.read_csv(path + filename)
        try:
            rounds = max(df['round'])
        except KeyError:
            rounds = max(df['index'])
        if ignore_initial_rounds >= rounds:
            ignore_initial_rounds = 0
            print 'kill'
        df = df.where((pd.notnull(df)), None)
        df.dropna(1, how='all', inplace=True)
        if filename.startswith('aggregate_'):
            plots.update(make_aggregate_graphs(df, filename, ignore_initial_rounds))
        else:
            try:
                if max(df.get('id', [0])) == 0:
                    plots.update(make_simple_graphs(df, filename, ignore_initial_rounds))
                else:
                    plots.update(make_panel_graphs(df, filename, ignore_initial_rounds))
            except ValueError:
                print(filename, 'not displayable: ValueError')

    script, div = components(plots)
    output = []

    for idname_title, graph in div.iteritems():
        idname, title = json.loads(idname_title)
        output.append({'idname': idname,  # can not stay i otherwise the cookie minimizing does not work
                       'title': title,
                       'graph': graph})

    output.extend(load_text(path))
    output.extend(load_text(path + '/../../'))
    output = sorted(output, key=lambda x: x['title'])
    return render_template('show_outcome.html', entries=output, desc=desc, setup=setup_dialog(rounds), script=script,
                           js_resources=INLINE.render_js(), css_resources=INLINE.render_css())


@app.route('/older_results')
def older_results():
    directory = os.path.abspath('./result')
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]
    return render_template('older_results.html', all_subdirs=all_subdirs)

@app.route('/del_simulation')
def del_simulation():
    path = request.args.get('subdir')
    try:
        shutil.rmtree(path)
    except OSError:
        print "could not remove", path
    return redirect(url_for('older_results'))

def generate(new_inputs, new_simulation, names=None, title=None, text=None):
    global inputs
    global simulation
    global gtitle
    global gtext

    if text is not None:
        gtext = text

    if title is not None:
        gtitle = title

    simulation = new_simulation

    ordered_inputs = new_inputs

    for parameter, value in ordered_inputs.items():
        element = {}
        element['name'] = parameter
        element['value'] = value
        try:
            element['title'] = names[parameter]
        except (TypeError, KeyError):
            element['title'] = parameter
        if type(value) == tuple:
            lvalue = sorted(value)
            element['min'] = lvalue[0]
            element['default'] = lvalue[1]
            element['max'] = lvalue[2]
        elif type(value) is float or type(value) is int:
            element['min'] = 0
            element['default'] = value
            element['max'] = value * 2

        if type(value) == tuple or type(value) is float or type(value) is int:
            if type(element['default']) is int and type(element['max']) is int:
                element['step'] = 1
                element['type'] = int
            else:
                element['type'] = float
                element['step'] = (element['max'] - element['min']) / 100

            content = """  {title}
                            <div class="mdl-grid">
                                <div class="mdl-cell mdl-cell--8-col">
                                    <input class="mdl-slider mdl-js-slider" type="range"
                                        min="{min}" max="{max}" value="{default}" id="sl{name}"
                                        step="{step}" oninput="change_text_field(this.value, '{name}')"
                                        onchange="change_text_field(this.value, '{name}')">
                                    </input>
                                </div>
                                <div class="mdl-cell mdl-cell--3-col">
                                    <div class="mdl-textfield mdl-js-textfield">
                                        <input class="mdl-textfield__input" type="text" id="{name}" name="{name}"
                                            onchange="change_slider_field(this.value, 'sl{name}')"
                                            value="{default}">
                                        </input>
                                    </div>
                                </div>
                            </div>""".format(**element)
        elif type(value) is bool:
            element['type'] = bool
            content = """<div>{title}</div><br> <label class="mdl-switch mdl-js-switch mdl-js-ripple-effect" for="{name}">
                          <input type="checkbox" id="{name}" class="mdl-switch__input" name={name} checked>
                          <span class="mdl-switch__label"></span>
                        </label>""".format(**element)
        elif type(value) is list:  # menu
            assert_all_of_the_same_type(value)
            element['type'] = type(value[0])
            element['value0'] = value[0]
            content = ("""<div>{title}</div><br><input list="{name}" value="{value0}" name="{name}">
                            <datalist id="{name}"> """
                      + "".join(['<option value="%s">' % item for item in value])
                      + """ </datalist> """).format(**element)
        elif type(value) is str:  # menu
            element['type'] = str
            content = """<div>{title}</div>
                         <div class="mdl-textfield mdl-js-textfield">
                           <textarea class="mdl-textfield__input" type="text"
                             rows= "1" id="{name}" name="{name}">{value}</textarea>
                           <label class="mdl-textfield__label" for="{name}">{value}</label>
                         </div>""".format(**element)
        elif value is None:
            content = parameter
        else:  # field
            raise SystemExit(str(value) + "not recognized")
        element['content'] = content
        if value is not None:
            inputs.append(element)

@app.route('/ignore_initial_rounds', methods=['POST'])
def ignore_initial_rounds():
    form = request.form.to_dict()
    session['ignore_initial_rounds'] = form['ignore_initial_rounds']
    return redirect(url_for('show_simulation'))

def setup_dialog(max_rounds):
    element = {}
    element['step'] = 25
    element['min'] = 0
    element['max'] = max_rounds
    element['default'] = int(session.get('ignore_initial_rounds', 0))
    element['url'] = url_for('ignore_initial_rounds')
    content = """ Ignore initial rounds, when generating the axises
                  <form  method="post"  action="{url}">
                    <div class="mdl-grid">
                        <div class="mdl-cell mdl-cell--8-col">
                            <input class="mdl-slider mdl-js-slider" type="range"
                                min="{min}" max="{max}" value="{default}" id="sldiscard_initial_rounds"
                                step="{step}" oninput="change_text_field(this.value, 'ignore_initial_rounds')"
                                onchange="change_text_field(this.value, 'ignore_initial_rounds')">
                            </input>
                        </div>
                        <div class="mdl-cell mdl-cell--3-col">
                            <div class="mdl-textfield mdl-js-textfield">
                                <input class="mdl-textfield__input" type="text" id="ignore_initial_rounds" name="ignore_initial_rounds"
                                    onchange="change_slider_field(this.value, 'sldiscard_initial_rounds')"
                                    value="{default}">
                                </input>
                            </div>
                        </div>
                    </div>
                    <input class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" type="submit" value="Update">
                    </input>
                  </form>""".format(**element)
    return content


def run(open=True, new=1):
    """ runs the web interface that starts the ABCE simulation. If open=True,
    (default) it opens a new window in the web browser if false you need to
    manually go to  http://127.0.0.1:5000/"""
    host = "127.0.0.1"
    port = find_free_port(host, 5000)
    if not opened:
        if open:
            if inputs:
                webbrowser.open("http://127.0.0.1:%i/" % port, new=new, autoraise=True)
            else:
                webbrowser.open("http://127.0.0.1:%i/show_simulation" % port, new=new, autoraise=True)
        if inputs:
            print "go to http://127.0.0.1:%i/" % port
        else:
            print "go to http://127.0.0.1:%i/show_simulation" % port
        global opened
        opened = True
        app.run(use_reloader=False, host=host, port=port)

# slider (slider-range)
# switch
# field
# menu (editable) (options)
# menu (fixed) (options)
# text

def assert_all_of_the_same_type(value):
    for item in value:
        if type(item) != type(value[0]):
            raise ValueError("all list values must be of the same type. If 5.5"
                             " is used 0.0 instead of 0 must be used: " + str(value))


if __name__ == '__main__':
    app.run()
