"""Internal helper package that creates graphs for gui and
simulation.graphs()"""
import random
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Range1d, LinearAxis, Span, Label
from bokeh.charts import Histogram
from bokeh.layouts import row


COLORS = ["red", "blue", "green", "black", "purple", "pink", "yellow",
          "orange", "pink", "Brown", "Cyan", "Crimson", "DarkOrange",
          "DarkSeaGreen", "DarkCyan", "DarkBlue", "DarkViolet", "Silver",
          "#0FCFC0", "#9CDED6", "#D5EAE7", "#F3E1EB", "#F6C4E1", "#F79CD4"]

TOOLS = "reset, pan, zoom_in, zoom_out, box_zoom, save, crosshair, hover"


def make_title(table_name, col):
    """makes a title out of table_name and column, cleaning it up"""
    return (table_name.replace('aggregate_', '')
            .replace('panel_', '')
            .replace('.csv', '')
            .replace('_log_', '')
            .replace('log_', '') +
            ' ' +
            col.replace('_ttl', ''))


def abce_figure(title, y_range=None):
    return figure(title=title, width=12, height=6,
                  sizing_mode='stretch_both',
                  output_backend='webgl',
                  toolbar_location='below', tools=TOOLS, y_range=y_range)


def make_aggregate_graphs(data, filename, ignore_initial_rounds):
    """Make timeseries graphs from aggregate or aggregate_ files, which contain
    _ttl, _mean and _std suffixes, to denote total, mean and
    standard deviation columns """
    data = clean_nans(data)
    print('make_aggregate_graphs', filename)
    # all columns exist 3 times, with _ttl, _mean and _std suffix
    # columns contains each type only once:
    columns = [col.replace('_ttl', '')
               for col in data.columns if col.endswith('_ttl')]
    index = data['round']
    titles = []
    plots = []
    for col in columns:
        if col == 'index':
            continue
        title = make_title(filename, col)
        plot = abce_figure(title)
        plot.yaxis.visible = False
        plot.legend.orientation = "top_left"

        try:
            plot.extra_y_ranges['std'] = y_range(col, 'std', data,
                                                 ignore_initial_rounds)

            plot.line(index, data[col + '_std'], legend='std', line_width=2,
                      line_color='red', y_range_name="std")
            plot.add_layout(LinearAxis(y_range_name="std"), 'right')
        except KeyError:
            pass

        plot.extra_y_ranges['ttl'] = y_range(col, 'ttl', data,
                                             ignore_initial_rounds)

        plot.line(index, data[col + '_ttl'], legend='mean/total', line_width=2,
                  line_color='blue', y_range_name="ttl")
        plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')
        try:
            plot.extra_y_ranges['mean'] = y_range(col, 'mean', data,
                                                  ignore_initial_rounds)
            plot.add_layout(LinearAxis(y_range_name="mean"), 'left')
        except KeyError:
            pass
        titles.append(title + ' (agg)')
        plots.append(plot)
    return titles, plots


def make_simple_graphs(data, filename, ignore_initial_rounds):
    """Make timeseries graphs from datafile, which has 'round' as
    index"""
    data = clean_nans(data)
    print('make_simple_graphs', filename)
    index = data['round']
    titles = []
    plots = []
    for col in data.columns:
        title = make_title(filename, col)
        if col not in ['round', 'id', 'index']:
            plot = abce_figure(title)
            plot.yaxis.visible = False
            plot.legend.orientation = "top_left"
            plot.extra_y_ranges['ttl'] = y_range(col, '', data,
                                                 ignore_initial_rounds)

            plot.legend.orientation = "top_left"
            plot.line(index, data[col], legend=col, line_width=2,
                      line_color='blue', y_range_name="ttl")
            plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')
            titles.append(title)
            plots.append(plot)

    return titles, plots


def make_histograms(data, filename):
    """Creates histograms from data. If several 'id's are present,
    several histograms for each id are created in the same plot """
    data = clean_nans(data)
    print('make_histograms', filename)
    titles = []
    plots = []
    num_graphs = 1
    if 'id' in data.columns:
        num_graphs = min(len(set(data['id'])), 6)
    else:
        data['id'] = 0
    for col in data.columns:
        if (col not in ['round', 'id', 'index', 'index_ttl'] and
                not col.endswith('_mean') and
                not col.endswith('_std')):
            title = make_title(filename, col)
            tplot = []
            for i in range(num_graphs):
                plot = Histogram(data[data['id'] == i][col],
                                 width=1200, height=600,
                                 sizing_mode='stretch_both')
                mean = data[data['id'] == i][col].mean()
                line = Span(location=mean,
                            dimension='height', line_color='blue',
                            line_width=1)
                plot.add_layout(line)
                label = Label(x=mean, y=0, text='mean: %f' % mean)
                plot.add_layout(label)
                tplot.append(plot)
            titles.append(title + ' (hist)')
            plots.append(row(tplot, sizing_mode='stretch_both'))
    return titles, plots


def make_panel_graphs(data, filename, ignore_initial_rounds):
    """ Creates panel graphs from data with 'round' and 'id' picks no more than 20
    samples to display"""
    data = clean_nans(data)
    print('make_panel_graphs', filename)
    num_individuals = max(data['id'])
    if num_individuals > 20:
        individuals = sorted(random.sample(range(max(data['id'])), 20))
    else:
        individuals = range(max(data['id']) + 1)
    data = data[data['id'].isin(individuals)]
    titles = []
    plots = []
    for col in data.columns:
        if col not in ['round', 'id', 'index']:
            y_range = (min(data[col][ignore_initial_rounds * len(individuals):]), max(data[col][ignore_initial_rounds * len(individuals):]))
            if y_range[0] == y_range[1]:
                y_range = (-1, 1)
            title = make_title(filename, col)
            plot = abce_figure(title, y_range=y_range)
            plot.legend.orientation = "top_left"
            for i, id in enumerate(individuals):
                index = data['round'][data['id'] == id]
                series = data[col][data['id'] == id]
                plot.line(index, series, legend=str(id),
                          line_width=2, line_color=COLORS[i])
            titles.append(title + ' (panel)')
            plots.append(plot)
    return titles, plots


def clean_nans(data):
    data = data.where((pd.notnull(data)), None)
    data.dropna(1, how='all', inplace=True)
    return data


def y_range(column, suffix, data, ignore_initial_rounds):
    """ returns a range that includes min and max y
    for values where x is above ignore_initial_rounds
    """
    if suffix != "":
        column = column + '_' + suffix

    relevant_subset = data[column].ix[ignore_initial_rounds:]
    if relevant_subset.min() == relevant_subset.max():
        return Range1d(relevant_subset.min(skipna=True) - 1,
                       relevant_subset.max(skipna=True) + 1)
    return Range1d(relevant_subset.min(skipna=True),
                   relevant_subset.max(skipna=True))
