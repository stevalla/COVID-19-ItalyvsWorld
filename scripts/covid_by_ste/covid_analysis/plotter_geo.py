import os
import plotly

import numpy as np
import plotly.graph_objs as go

from definitions import COUNTRY, STATE, DIRS, STATUS_TYPES


class PlotterGeo:

    def __init__(self, data):
        self._data = data

    def plot_map(self, data_):
        data_['country'] = self._world_map_country_names(data_)
        data = data_.groupby('iso3').sum()
        domains = (dict(x=[0.0, 0.5], y=[0.0, 1.0]),
                   dict(x=[0.5, 1.0], y=[0.0, 1.0]))
        subtitle_pos = [0.1, 0.9]
        annotations_t = {"y": 0.99,  "font": {"size": 30}, "xref": "paper",
                         "yref": "paper", "xanchor": "center",
                         "yanchor": "bottom", "showarrow": False}

        layout = {}
        plots = []
        annotations = []
        for i, status in enumerate(STATUS_TYPES):
            sizes = np.log(data_[status].replace(0, 1)) / np.log(1.5)
            colors = np.log(data[status].replace(0, 1)) / np.log(1.3)
            geo = 'geo{}'.format(str(i+1) if i > 0 else '')
            annotations.append(annotations_t.copy())
            annotations[i]['x'] = subtitle_pos[i]
            annotations[i]['text'] = status.capitalize()
            plots.append(dict(
                type='choropleth',
                z=colors,
                locations=data.index.values,
                locationmode='ISO-3',
                colorscale='Sunsetdark',
                hoverinfo='none',
                geo=geo,
                colorbar=dict(
                    title='Cases',
                    titleside='top',
                    tickmode='array',
                    tickvals=[np.min(colors), np.max(colors)],
                    ticktext=['min', 'max'],
                    tickfont=dict(size=22)
                ),
                marker=dict(line=dict(color='rgb(250,250,200)', width=0.5))
            ))
            plots.append(dict(
                type='scattergeo',
                lon=data_['Long'],
                lat=data_['Lat'],
                geo=geo,
                text=data_['country'],
                mode='markers',
                showlegend=False,
                marker=dict(size=sizes, opacity=0.3, color='cyan')
            ))
            layout[geo] = dict(
                projection_type="orthographic",
                oceancolor="MidNightBlue",
                countrycolor="white",
                coastlinecolor="white",
                showocean=True,
                showcoastlines=True,
                showcountries=True,
                showland=True,
                domain=domains[i],
                showlakes=True,
            )
        fig = go.Figure(data=plots, layout=layout)
        fig.update_layout(
            autosize=True,
            hovermode="closest",
            title=dict(
                text='<b>COVID spread in the world',
                y=0.99, x=0.5, xanchor='center', yanchor='top'
            ),
            font=dict(size=35),
            annotations=annotations,
        )
        fig.update_yaxes(automargin=True)
        fig.write_html(os.path.join(DIRS['result'], 'world_map.html'))

    def _world_map_country_names(self, data):
        countries = []
        for i in data.index:
            name = data.loc[i, COUNTRY]
            if not data.loc[i, STATE] is np.nan:
                name += ' {}'.format(data.loc[i, STATE])
            countries.append(name)
        return countries

