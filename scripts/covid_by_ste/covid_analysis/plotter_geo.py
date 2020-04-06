import os
import logging

import numpy as np
import plotly.graph_objs as go
import chart_studio.plotly as cs

from utils import merge_pdf
from definitions import COUNTRY, STATE, DIRS, STATUS_TYPES, yesterday

log = logging.getLogger(__name__)

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
        footnote = {"x": 1.1, 'y': -0.12, "font": {"size": 18},
                    "xref": "paper", "yref": "paper", "xanchor": "right",
                    "yanchor": "bottom", "showarrow": False,
                    "text": "Last update at {}".format(yesterday())}

        layout = {}
        plots = []
        frames = []
        annotations = [footnote]
        for i, status in enumerate(STATUS_TYPES):
            sizes = np.log(data_[status].replace(0, 1)) / np.log(1.5)
            colors = np.log(data[status].replace(0, 1)) / np.log(1.3)
            geo = 'geo{}'.format(str(i+1) if i > 0 else '')
            annotations.append(annotations_t.copy())
            annotations[i + 1]['x'] = subtitle_pos[i]
            annotations[i + 1]['text'] = status.capitalize()
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
                projection_rotation_lon=0,
                showocean=True,
                showcoastlines=True,
                showcountries=True,
                showland=True,
                domain=domains[i],
                showlakes=True
            )
        lon_range = list(np.arange(0, 180, 3)) + list(np.arange(-180, 0, 3))
        for lon in lon_range:
            frames.append(dict(
                layout=dict(geo=dict(center_lon=lon,
                                     projection_rotation_lon=lon),
                            geo2=dict(center_lon=lon,
                                      projection_rotation_lon=lon)))
            )
        fig = go.Figure(data=plots, layout=layout, frames=frames)
        fig.update_layout(
            autosize=True,
            hovermode="closest",
            title=dict(
                text='<b>COVID SPREAD',
                y=0.99, x=0.5, xanchor='center', yanchor='top'
            ),
            font=dict(size=35),
            annotations=annotations,
            transition=dict(duration=0.5)
        )
        fig.update_yaxes(automargin=True)
        fig.write_html(os.path.join(DIRS['result'], 'geo/world_map.html'))
        fig.write_image(os.path.join(DIRS['result'], 'tmp.pdf'))
        merge_pdf('world_map_3d.pdf')
        os.rename(os.path.join(DIRS['result'], 'world_map_3d.pdf'),
                  os.path.join(DIRS['result'], 'geo/world_map_3d.pdf'))
        url = cs.plot(fig, filename='privacy-public', sharing='public',
                      auto_open=False)
        log.info('World map at ', url)

    def _world_map_country_names(self, data):
        countries = []
        for i in data.index:
            name = data.loc[i, COUNTRY]
            if not data.loc[i, STATE] is np.nan:
                name += ' {}'.format(data.loc[i, STATE])
            countries.append(name)
        return countries
