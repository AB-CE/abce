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


def make_title(title, col):
    return (title.replace('aggregate_', '')
                 .replace('panel_', '')
                 .replace('.csv', '')
                 .replace('_log_', '')
                 .replace('log_', '')
            + ' '
            + col.replace('_ttl', ''))


def make_aggregate_graphs(df, filename, ignore_initial_rounds):
    df = clean_nans(df)
    print('make_aggregate_graphs', filename)
    # all columns exist 3 times, with _ttl, _mean and _std suffix
    # columns contains each type only once:
    columns = [col.replace('_ttl', '')
               for col in df.columns if col.endswith('_ttl')]
    index = df['round']
    titles = []
    plots = []
    for col in columns:
        if col == 'index':
            continue
        title = make_title(filename, col)
        plot = figure(title=title, sizing_mode='stretch_both',
                      output_backend='webgl',
                      toolbar_location='below', tools=TOOLS)
        plot.yaxis.visible = None
        plot.legend.orientation = "top_left"

        try:
            plot.extra_y_ranges['std'] = y_range(col, 'std', df,
                                                 ignore_initial_rounds)

            plot.line(index, df[col + '_std'], legend='std', line_width=2,
                      line_color='red', y_range_name="std")
            plot.add_layout(LinearAxis(y_range_name="std"), 'right')
        except KeyError:
            pass

        plot.extra_y_ranges['ttl'] = y_range(col, 'ttl', df,
                                             ignore_initial_rounds)

        plot.line(index, df[col + '_ttl'], legend='mean/total', line_width=2,
                  line_color='blue', y_range_name="ttl")
        plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')
        try:
            plot.extra_y_ranges['mean'] = y_range(col, 'mean', df,
                                                  ignore_initial_rounds)
            plot.add_layout(LinearAxis(y_range_name="mean"), 'left')
        except KeyError:
            pass
        titles.append(title + ' (agg)')
        plots.append(plot)
    return titles, plots


def make_simple_graphs(df, filename, ignore_initial_rounds):
    df = clean_nans(df)
    print('make_simple_graphs', filename)
    index = df['round']
    titles = []
    plots = []
    for col in df.columns:
        title = make_title(filename, col)
        if col not in ['round', 'id', 'index']:
            plot = figure(title=title, sizing_mode='stretch_both',
                          output_backend='webgl',
                          toolbar_location='below', tools=TOOLS)
            plot.yaxis.visible = None
            plot.legend.orientation = "top_left"
            plot.extra_y_ranges['ttl'] = y_range(col, '', df,
                                                 ignore_initial_rounds)

            plot.legend.orientation = "top_left"
            plot.line(index, df[col], legend=col, line_width=2,
                      line_color='blue', y_range_name="ttl")
            plot.add_layout(LinearAxis(y_range_name="ttl"), 'left')
            titles.append(title)
            plots.append(plot)

    return titles, plots


def make_histograms(df, filename, ignore_initial_rounds):
    df = clean_nans(df)
    print('make_histograms', filename)
    titles = []
    plots = []
    num_graphs = 1
    if 'id' in df.columns:
        num_graphs = min(len(set(df['id'])), 6)
    else:
        df['id'] = 0
    for col in df.columns:
        if (col not in ['round', 'id', 'index', 'index_ttl']
                and not col.endswith('_mean')
                and not col.endswith('_std')):
            title = make_title(filename, col)
            tplot = []
            for i in range(num_graphs):
                plot = Histogram(df[df['id'] == i][col],
                                 sizing_mode='stretch_both')
                mean = df[df['id'] == i][col].mean()
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


def make_panel_graphs(df, filename, ignore_initial_rounds):
    # clean nan
    df = clean_nans(df)

    print('make_panel_graphs', filename)

    if max(df['id']) > 20:
        individuals = sorted(random.sample(range(max(df['id'])), 20))
    else:
        individuals = range(max(df['id']) + 1)
    df = df[df['id'].isin(individuals)]
    titles = []
    plots = []
    for col in df.columns:
        if col not in ['round', 'id', 'index']:
            title = make_title(filename, col)
            plot = figure(title=title, sizing_mode='stretch_both',
                          output_backend='webgl',
                          toolbar_location='below', tools=TOOLS)

            plot.legend.orientation = "top_left"
            for i, id in enumerate(individuals):
                index = df['round'][df['id'] == id]
                series = df[col][df['id'] == id]
                plot.line(index, series, legend=str(id),
                          line_width=2, line_color=COLORS[i])
            titles.append(title + ' (panel)')
            plots.append(plot)
    return titles, plots


def clean_nans(df):
    df = df.where((pd.notnull(df)), None)
    df.dropna(1, how='all', inplace=True)
    return df


def y_range(column, suffix, df, ignore_initial_rounds):
    """ returns a range that includes min and max y
    for values where x is above ignore_initial_rounds
    """
    if suffix != "":
        column = column + '_' + suffix

    relevant_subset = df[column].ix[ignore_initial_rounds:]
    if relevant_subset.min() != relevant_subset.max():
        return Range1d(relevant_subset.min(skipna=True),
                       relevant_subset.max(skipna=True))
    else:
        return Range1d(relevant_subset.min(skipna=True) - 1,
                       relevant_subset.max(skipna=True) + 1)
