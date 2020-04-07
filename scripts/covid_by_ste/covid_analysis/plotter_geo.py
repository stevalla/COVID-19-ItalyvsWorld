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

    def plot_world_map_3d(self, world_data):
        world_data['country'] = self._world_map_country_names(world_data)
        data = world_data.groupby('iso3').sum()
        domains = (dict(x=[0.0, 0.5], y=[0.0, 1.0]),
                   dict(x=[0.5, 1.0], y=[0.0, 1.0]))
        subtitle_pos = [0.1, 0.9]
        annotations_t = {"y": 0.99,  "font": {"size": 30}, "xref": "paper",
                         "yref": "paper", "xanchor": "center",
                         "yanchor": "bottom", "showarrow": False}
        footnote = {"x": 1.1, 'y': -0.12, "font": {"size": 18},
                    "xref": "paper", "yref": "paper", "xanchor": "right",
                    "yanchor": "bottom", "showarrow": False,
                    "text": "Last update at {}".format(yesterday(ts=True))}

        layout = {}
        plots = []
        frames = []
        annotations = [footnote]
        for i, status in enumerate(STATUS_TYPES):
            sizes = np.log(world_data[status].replace(0, 1)) / np.log(1.5)
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
                lon=world_data['Long'],
                lat=world_data['Lat'],
                geo=geo,
                text=world_data['country'],
                mode='markers',
                showlegend=False,
                marker=dict(
                    size=sizes,
                    opacity=0.3,
                    color='cyan',
                    line=dict(width=0)
                )
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
        url = self._store_result(fig, 'world_map_3d', 'html')
        log.info('World map 3D at {}'.format(url))

    def plot_world_map(self, world_data):
        world_data['country'] = self._world_map_country_names(world_data)
        footnote = {"x": 0.9, 'y': 1, "font": {"size": 18},
                    "xref": "paper", "yref": "paper", "xanchor": "right",
                    "yanchor": "bottom", "showarrow": False,
                    "text": "Last update at {}".format(yesterday(ts=True))}

        sizes = np.log(world_data['confirmed'].replace(0, 1)) / np.log(1.5)

        fig = go.Figure(
            data=[dict(
                type='scattergeo',
                lon=world_data['Long'],
                lat=world_data['Lat'],
                geo='geo',
                text=world_data['country'],
                mode='markers',
                showlegend=False,
                marker=dict(
                    size=sizes,
                    opacity=0.7,
                    color='red',
                    line=dict(width=0)
                )
            )],
            layout=dict(geo=dict(
                projection_type="natural earth",
                visible=False,
                oceancolor="white",
                countrycolor="rgb(47, 45, 42)",
                landcolor="rgb(21, 19, 17)",
                projection_rotation_lon=0,
                showocean=True,
                showcountries=True,
                showland=True,
                showlakes=True,
                showrivers=True,
                lakecolor='rgb(46, 100, 117, 0.4)',
                rivercolor='rgb(46, 100, 117, 0.1)'
            ))
        )

        fig.update_layout(
            autosize=True,
            hovermode="closest",
            font=dict(size=35),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            annotations=[footnote],
        )
        fig.update_yaxes(automargin=True)
        url = self._store_result(fig, 'world_map_2d', 'png')
        log.info('World map at {}'.format(url))

    def _world_map_country_names(self, data):
        countries = []
        for i in data.index:
            name = data.loc[i, COUNTRY]
            if not data.loc[i, STATE] is np.nan:
                name += ' {}'.format(data.loc[i, STATE])
            countries.append(name)
        return countries

    def _store_result(self, fig, title, ext):
        if ext == 'html':
            fig.write_html(os.path.join(DIRS['result'],
                                        'geo/{}.html'.format(title)))
        elif ext == 'png':
            fig.write_image(os.path.join(DIRS['result'],
                                         'geo/{}.png'.format(title)))
        else:
            raise ValueError('Extension not supported')

        fig.write_image(os.path.join(DIRS['result'], 'tmp.pdf'))
        merge_pdf('{}.pdf'.format(title))
        os.rename(os.path.join(DIRS['result'], '{}.pdf'.format(title)),
                  os.path.join(DIRS['result'], 'geo/{}.pdf'.format(title)))
        url = cs.plot(fig, filename='privacy-public', sharing='public',
                      auto_open=False)
        return url
