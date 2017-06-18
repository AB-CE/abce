from bokeh.plotting import figure
from bokeh.models import Range1d, LinearAxis
from bokeh.io import gridplot
import json
import datetime
import random


colors = ["red", "blue", "green", "black", "purple", "pink",
          "yellow", "orange", "pink", "Brown", "Cyan", "Crimson",
          "DarkOrange", "DarkSeaGreen", "DarkCyan", "DarkBlue", "DarkViolet", "Silver",
          "#0FCFC0", "#9CDED6", "#D5EAE7", "#F3E1EB", "#F6C4E1", "#F79CD4"]


def make_title(title, col):
    return title.replace('aggregate_', '').replace('panel_', '').replace('.csv', '') + ' ' + col


def make_aggregate_graphs(df, filename, ignore_initial_rounds):
    print('make_aggregate_graphs', filename)
    columns = [col for col in df.columns if not col.endswith('_std')
                                         and not col.endswith('_mean')
                                         and not col in ['index', 'round', 'id', 'date']]
    plots = {}
    try:
        index = df['date'].apply(lambda sdate: datetime.date(*[int(c) for c in sdate.split('-')]))
        x_axis_type = "datetime"
    except KeyError:
        index = df['round']
        x_axis_type = "linear"
    for col in columns:
        title = make_title(filename, col)
        plot = figure(title=title, responsive=True, webgl=False, x_axis_type=x_axis_type,
                      tools="pan, wheel_zoom, box_zoom, save, crosshair, hover")
        plot.yaxis.visible = None
        plot.legend.orientation = "top_left"

        try:
            if df[col + '_std'].min() != df[col + '_std'].max():
                plot.extra_y_ranges['std'] = Range1d(df[col + '_std'].ix[ignore_initial_rounds:].min(skipna=True),
                                                     df[col + '_std'].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['std'] = Range1d(df[col + '_std'].ix[ignore_initial_rounds:].min(skipna=True) - 1,
                                                     df[col + '_std'].ix[ignore_initial_rounds:].max(skipna=True) + 1)
            plot.line(index, df[col + '_std'],
                      legend='std', line_width=2, line_color='red', y_range_name="std")
            plot.add_layout(LinearAxis(y_range_name="std"), 'right')
        except KeyError:
            pass

        if df[col].min(skipna=True) != df[col].max(skipna=True):
            plot.extra_y_ranges['ttl'] = Range1d(df[col].ix[ignore_initial_rounds:].min(skipna=True),
                                                 df[col].ix[ignore_initial_rounds:].max(skipna=True))
        else:
            plot.extra_y_ranges['ttl'] = Range1d(df[col].ix[ignore_initial_rounds:].min(skipna=True) - 1,
                                                 df[col].ix[ignore_initial_rounds:].max(skipna=True) + 1)

        plot.line(index, df[col],
                  legend='mean/total', line_width=2, line_color='blue', y_range_name="ttl")
        plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')
        try:
            if df[col + '_mean'].min() != df[col + '_mean'].max():
                plot.extra_y_ranges['mean'] = Range1d(df[col + '_mean'].ix[ignore_initial_rounds:].min(skipna=True),
                                                      df[col + '_mean'].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['mean'] = Range1d(df[col + '_mean'].ix[ignore_initial_rounds:].min(skipna=True) - 1,
                                                      df[col + '_mean'].ix[ignore_initial_rounds:].max(skipna=True) + 1)
            # plot.line(index, df[col],
            #          legend='mean', line_width=2, line_color='green', y_range_name="mean")
            plot.add_layout(LinearAxis(y_range_name="mean"), 'left')
        except KeyError:
            pass
        plots[json.dumps((plot.ref['id'], title + ' (agg)'))] = plot
    return plots


def make_simple_graphs(df, filename, ignore_initial_rounds):
    print('make_simple_graphs', filename)
    plots = {}
    try:
        index = df['date'].apply(lambda sdate: datetime.date(*[int(c) for c in sdate.split('-')]))
        x_axis_type = "datetime"
    except KeyError:
        index = df['round']
        x_axis_type = "linear"
    for col in df.columns:
        if col not in ['round', 'id', 'index', 'date']:
            title = make_title(filename, col)
            plot = figure(title=title, responsive=True, webgl=False, x_axis_type=x_axis_type,
                          tools="pan, wheel_zoom, box_zoom, save, crosshair, hover")
            plot.yaxis.visible = None
            plot.legend.orientation = "top_left"
            if df[col].min(skipna=True) != df[col].max(skipna=True):
                plot.extra_y_ranges['ttl'] = Range1d(df[col].ix[ignore_initial_rounds:].min(skipna=True),
                                                     df[col].ix[ignore_initial_rounds:].max(skipna=True))
            else:
                plot.extra_y_ranges['ttl'] = Range1d(df[col].ix[ignore_initial_rounds:].min(skipna=True) - 1,
                                                     df[col].ix[ignore_initial_rounds:].max(skipna=True) + 1)

            plot.legend.orientation = "top_left"
            plot.line(index, df[col], legend=col, line_width=2, line_color='blue', y_range_name="ttl")
            plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')

            plots[json.dumps((plot.ref['id'], title))] = plot
    return plots


def make_panel_graphs(df, filename, ignore_initial_rounds):
    print('make_panel_graphs', filename)
    if 'date' in df.columns:
        x_axis_type = "datetime"
    else:
        x_axis_type = "linear"

    if max(df['id']) > 20:
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
