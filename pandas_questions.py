"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res = pd.merge(regions, departments, how='inner', left_on="code",
                   right_on="region_code")
    res = res.rename(columns={
        "code_x": "code_reg",
        "name_x": "name_reg",
        "code_y": "code_dep",
        "name_y": "name_dep"
    })

    return res[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum_cp = referendum.copy()
    referendum_cp = referendum_cp[
        (referendum_cp['Department name'] != 'GUADELOUPE') &
        (referendum_cp['Department name'] != 'REUNION') &
        (referendum_cp['Department name'] != 'TAHITI')]

    referendum_cp = referendum_cp[
        ~referendum_cp["Department code"].str.contains("Z")]

    referendum_cp['Department code'] = \
        referendum_cp['Department code'].astype(str).str.zfill(2)

    res_ref_areas = pd.merge(referendum_cp, regions_and_departments,
                             how='left', left_on="Department code",
                             right_on="code_dep")

    return res_ref_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # recup ordre des regions par code_reg
    temp = referendum_and_areas["name_reg"]
    temp.index = referendum_and_areas["code_reg"]
    index_order = temp.sort_values().index.unique()

    res = referendum_and_areas[['name_reg', 'Registered', 'Abstentions',
                                'Null', 'Choice A', 'Choice B']]
    res = res.groupby('name_reg').sum()
    res['name_reg'] = res.index
    res = res[['name_reg', 'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']]
    res.index = index_order
    res = res.sort_values('name_reg')
    res.index = index_order
    return res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gdf = gpd.read_file("./data/regions.geojson")

    geo_df = gdf.merge(
        referendum_result_by_regions,
        how="left",
        left_on="code",
        right_index=True
    )

    geo_df["ratio"] = \
        geo_df["Choice A"] / (geo_df["Choice B"] + geo_df["Choice A"])

    # fig, ax = plt.subplots()

    # geo_df.plot(
    #     column="ratio",
    #     cmap="OrRd",
    #     legend=True,
    #     ax=ax,
    # )

    # ax.set_title("Ratio par région")
    # ax.axis("off")

    # plt.show()

    return geo_df


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
