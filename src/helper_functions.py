import re
import pandas as pd
from typing import List, Dict

def get_text_data(filepath: str, filename: str, delim: str) -> List[str]:
    """Get text data stored in a text file and return a list of values,
       split by the specified delimiter.

    Args:
        filepath (str): File path of text file.
        filename (str): File name of text file.
        delim (str): Delimiter used in text file.

    Returns:
        List[str]: List of text values.
    """
    with open("{}/{}".format(filepath, filename), "r", encoding="utf-8") as f:
        data = f.read()
    return data.split(delim)

def clean_plots(plot_list: List[str], charlim: bool = False) -> List[str]:
    """Clean list of plot strings. Do the following:
       - Only keep plots that end in "." but do not end in "..."
       - Strip any leading whitespace
       - If any delimiters exist within the text, replacethem with ""
       - If chalim = True, only keep plots with less than 280 characters

    Args:
        plot_list (List[str]): The initial list of generated plots.
        charlim (bool, optional): If True, only keep plots 280 characters or less. Defaults to False.

    Returns:
        List[str]: Cleaned plot list, dropping the first element since it often is incomplete.
    """
    clean_plots = []
    for i in range(len(plot_list)):
        plot = plot_list[i]
        if plot[-1:] == "." and plot[-3:] != "...":#and re.search("^((?![<|\||>|\n]).)*$", plot):
            plot = plot.lstrip(" ")
            plot = re.sub("\<\|endoftext\|\>", "", plot)
            if charlim:
                if len(plot) <= 280:
                    clean_plots.append(plot)
            else:
                clean_plots.append(plot)
    return clean_plots[1:]

def get_cleaner_plot_dict(plot_list: List[str], filter_words: List[str]) -> Dict[str, str]:
    """Another step in cleaning plots. Only plots with titles not having words in filter_words
       are kept.

    Args:
        plot_list (List[str]): List of plots to clean.
        filter_words (List[str]): List of filter words.

    Returns:
        Dict[str, str]: Dictionary with k = title, v = plot.
    """
    plot_d = {}
    for i in plot_list:
        try:
            splt = i.split("\n")[0:3:2]
            if not re.search("|".join(filter_words), splt[0]):
                plot_d[splt[0]] = splt[1]
        except:
            print("error:", i)
    return plot_d

def create_plots_dataframe(d: Dict[str, str]) -> pd.DataFrame:
    """Creates a dataframe from generated plots, with a generic id,
       along with the title and plot.

    Args:
        d (Dict[str, str]): Dictionary with k = title, v = plot.

    Returns:
        pd.DataFrame: Pandas dataframe.
    """
    titles = list(d.keys())
    plots = list(d.values())
    ids = [i for i in range(len(d))]
    temp_d = {"id": ids, "title": titles, "plot": plots}
    return pd.DataFrame(data=temp_d)