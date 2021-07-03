"""Helper functions used in prepping training data, and cleaning generated text for PlotBot."""

import re
import json
from collections import Counter
from typing import Dict, List, Tuple

import pandas as pd


def print_plot_lens(plot_list: List[str]) -> None:
    """Print a few lines to show numbers of unique plots and duplicates.

    Args:
        plot_list (List[str]): List of plots.

    Returns:
        None.
    """
    n_plots = len(plot_list)
    n_unique = len(list(set(plot_list)))
    n_dupe = n_plots - n_unique
    print("number of plots       :", n_plots)
    print("number of unique plots:", n_unique)
    print("number of duplicates  :", n_dupe)


def get_n_most_common(val_list: List[str], n: int) -> Tuple[str, int]:
    """Get the most common values in a list, and return the top n
       values as a tuple.

    Args:
        val_list (List[str]): List of values.
        n (int): Number of values to return.

    Returns:
        Tuple[str, int]: Tuple of value, number of occurrences in list.
    """
    count_d = {}
    for v in val_list:
        if v in count_d.keys():
            count_d[v] += 1
        else:
            count_d[v] = 1
    k = Counter(count_d)
    return k.most_common(n)


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
        charlim (bool, optional): If True, only keep plots 280
            characters or less. Defaults to False.

    Returns:
        List[str]: Cleaned plot list, dropping the first element since it often is incomplete.
    """
    cleaned_plots = []
    for i in range(len(plot_list)):
        plot = plot_list[i]
        if (
                plot[-1:] == "." and plot[-3:] != "..."
        ):  # and re.search("^((?![<|\||>|\n]).)*$", plot):
            plot = plot.lstrip(" ")
            plot = re.sub("\<\|endoftext\|\>", "", plot)
            if charlim:
                if len(plot) <= 280:
                    cleaned_plots.append(plot)
            else:
                cleaned_plots.append(plot)
    return cleaned_plots[1:]


def get_cleaner_plot_dict(
        plot_list: List[str], filter_words: List[str]
) -> Dict[str, str]:
    """Another step in cleaning plots. Only plots with titles not having words in filter_words
       are kept.

    Args:
        plot_list (List[str]): List of plots to clean.
        filter_words (List[str]): List of filter words.

    Returns:
        Dict[str, str]: Dictionary of titles: plots.
    """
    plot_d = {}
    for i in plot_list:
        try:
            splt = i.split("\n")[0:3:2]
            if not re.search("|".join(filter_words), splt[0]):
                plot_d[splt[0]] = splt[1]
        except:
            continue
    return plot_d


def create_plots_dataframe(d: Dict[str, str]) -> pd.DataFrame:
    """Creates a dataframe from generated plots,
       along with the title and plot.

    Args:
        d (Dict[str, str]): Dictionary of titles: plots.

    Returns:
        pd.DataFrame: Pandas dataframe.
    """
    titles = list(d.keys())
    plots = list(d.values())
    temp_d = {"title": titles, "plot": plots}
    return pd.DataFrame(data=temp_d)


def filter_plots(
        plot_dict: Dict[str, str], search_words: List[str], deny_words: List[str]
) -> Dict[str, str]:
    """Get a dictionary of title: plots for all plots that contain keywords in
       the search_words list, and do not contain words from the deny_words list.

    Args:
        plot_dict (Dict[str, str]): Dictionary of titles: plots.
        search_words (List[str]): List of words to match plots containing any of these words.
        deny_words (List[str]): List of words to reject plots containing any of these words.

    Returns:
        Dict[str, str]: Dictionary of filtered results with titles: plots.
    """
    filtered_d = {}
    for k, v in plot_dict.items():
        temp = k + " " + v
        temp = re.sub("[^a-zA-z|\s]", "", temp)
        temp = temp.split(" ")
        while True:
            for word in temp:
                if re.match(
                        "|".join(search_words), word, re.IGNORECASE
                ) and not re.match("|".join(deny_words), word, re.IGNORECASE):
                    filtered_d[k] = v
                    break
            break

    return filtered_d


def update_json(filepath: str, filename: str, new_plots_d: Dict[str, str]) -> None:
    """Pull data from plots json file, add data from new_plots_d, and write data
       back to json file.

    Args:
        filepath (str): Folder with json file.
        filename (str): Name of json file.
        new_plots_d (Dict[str, str]): Dictionary of new plots with titles: plots.
    """
    json_path = "{}/{}.json".format(filepath, filename)
    # get all plots in json file
    with open(json_path, "r") as f:
        data = json.load(f)
    f.close()
    # update dictionary data from json file and write new+old data back to the json file
    data.update(new_plots_d)
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)
    f.close()
