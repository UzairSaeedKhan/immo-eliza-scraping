import polars as pl

def save_to_csv(df, path):
    """
    Saves a dataframe as a CSV file to the path provided.
    """

    df.write_csv(path)

def join_two_dfs_by_property_id(df1, df2): 
    """
    Executes an inner join of two dataframes by the property_id column.
    Used to create the final dataframe after scraping all properties.
    """

    df1_clean = df1.with_columns(
        pl.col("property_id")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_lowercase()
    )
    df2_clean = df2.with_columns(
        pl.col("property_id")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_lowercase()
    )
    joined_df = df1_clean.join(df2_clean, on="property_id", how="inner")
    return joined_df
