import numpy as np
import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
from functools import reduce
import dash_core_components as dcc
from typing import List, Dict


def generate_marks(min, max, step):
    marks = {}
    for i in np.arange(min, max + 1, step):
        if i % max == 0:
            marks[int(i)] = str(round(i, 2))
        else:
            marks[i] = str(round(i, 2))
    return marks


def get_std_figure(title, data_groups):
    def get_band_traces(name, data, color):
        # calculate bounds
        mean_data, ucb_data, lcb_data = get_deviations(data)

        x = np.arange(mean_data.shape[0])
        upper_bound = go.Scatter(
            name=name,
            x=x,
            y=ucb_data,
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            fillcolor=color,
            fill='tonexty',
            legendgroup=name,
            showlegend=False, )

        trace = go.Scatter(
            name=name,
            x=x,
            y=mean_data,
            mode='lines',
            line=dict(color=color),
            fillcolor=color,
            fill='tonexty',
            legendgroup=name)

        lower_bound = go.Scatter(
            name=name,
            x=x,
            y=lcb_data,
            fillcolor=color,
            line=dict(width=0),
            mode='lines',
            legendgroup=name,
            showlegend=False, )

        # Trace order can be important
        # with continuous error bars
        trace_data = [lower_bound, trace, upper_bound]

        return trace_data

    trace_data = list(
        reduce(lambda x, y: x + get_band_traces(y[0][0], y[0][1], y[1]), zip(data_groups.items(), DEFAULT_PLOTLY_COLORS), []))
    fig = go.Figure(data=trace_data, layout={
        'plot_bgcolor': '#ffffff',
        'showlegend': True
    })

    # center the title
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return fig


def get_deviations(data):
    m, sd = np.mean(data, axis=0), np.std(data, axis=0)
    return m, m - sd, m + sd


def get_line_graph(id, series: List[Dict], title) -> dcc.Graph:
    def create_one_series(name, data) -> Dict:
        series = {"x": list(range(len(data))), 'y': data, 'type': 'linear', 'name': name}
        return series

    def get_series_data(series) -> List:
        return [create_one_series(exp["experiment_id"], exp["data"]) for exp in series]

    graph = dcc.Graph(
        id=id,
        figure={
            'data': get_series_data(series),
            'layout': {
                'title': title,
            }
        }
    )
    return graph


def get_band_graph(id, series_groups: Dict, title) -> dcc.Graph:
    band_graph = dcc.Graph(
        id=id,
        figure=get_std_figure(title, series_groups)
    )
    return band_graph