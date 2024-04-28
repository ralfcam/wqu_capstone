import pandas as pd
import os


def add_file_content_column(df, path_column, new_column, base_dir="data/text/"):
    """
    Adds a new column to the DataFrame with the content of the text files specified in an existing column.

    Parameters:
    - df (pd.DataFrame): The DataFrame to modify.
    - path_column (str): The name of the column containing the file paths.
    - new_column (str): The name of the new column to store the file contents.

    Returns:
    - pd.DataFrame: The modified DataFrame with the new column.
    """

    def read_file_content(path):
        try:
            path = base_dir + path.split("data/")[1].replace("/", "-").replace("htm", "txt")
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return pd.NA

    df[new_column] = df[path_column].apply(read_file_content)
    return df


releases = pd.read_csv("data/releases/recent.csv", index_col="accessionNumber")
releases = add_file_content_column(releases, 'report_url', 'report_content')

rel_reports = releases[['form', 'ticker', 'reportDate', 'acceptanceDateTime', 'report_content']].dropna()  # 'filingDate',
rel_reports["reportDate"] = pd.to_datetime(rel_reports["reportDate"], format='%Y-%m-%d')

releases_Q_reports = rel_reports[rel_reports["form"] == "10-Q"].dropna()
del releases_Q_reports["form"]
releases_Q_reports.to_csv("data/structured_reports/Q_reports.csv", index=False)

releases_K_reports = rel_reports[rel_reports["form"] == "10-K"].dropna()
del releases_K_reports["form"]
releases_K_reports.to_csv("data/structured_reports/K_reports.csv", index=False)