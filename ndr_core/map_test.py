import folium
import pandas as pd


def get_map(coords_list, zoom_start=7):
    stores = [(1234568, 'Place1', -14.992287656550435, 167.0315877440207),
              (3456788, 'Place2', -17.649002027962336, 168.30600176288098)]
    df = pd.DataFrame(coords_list, columns=['ID', 'NAME', 'LAT', 'LNG'])
    mymap = folium.Map(location=[df['LAT'].mean(), df['LNG'].mean()])
    marker_group = folium.FeatureGroup(name='Markers')

    for row in df.itertuples():
        location = row[3], row[4]

        marker = folium.Marker(location=location)
        marker_group.add_child(marker)
        mymap.add_child(marker)

    mymap.fit_bounds(marker_group.get_bounds())
    return mymap._repr_html_()
