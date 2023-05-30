



def create_lines_between_centroids(LAU=None, Nodes=None):
    _res_df = pandas.DataFrame(columns=["Pressure", "Geometry", "Length"])

    geod = Geod(ellps="WGS84")

    for index, row in Nodes.iterrows():
        if row['2050'] != 0:
            point1 = LAU.loc[LAU.LAU_NAME == row["Node 1"]].geometry.item().centroid
            point2 = LAU.loc[LAU.LAU_NAME == row["Node 2"]].geometry.item().centroid
            LineString = geometry.LineString([point1, point2])
            Length = geod.geometry_length(LineString) / 1000
            item = {
                "Pressure": [row["Pressure level"]],
                "Geometry": [LineString],
                "Length": [Length],
            }
            _new = pandas.DataFrame(data=item)
            _res_df = pandas.concat([_res_df, _new])

    _res_df = gpd.GeoDataFrame(_res_df, geometry=_res_df["Geometry"])
    _res_df.set_crs(epsg=4326, inplace=True)
    _res_df.reset_index(inplace=True)
    _res_df.drop(columns=["Geometry", "index"], inplace=True)

    return _res_df