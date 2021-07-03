"""Clean and filter generated text from GPT-2 model"""
import argparse
import helper_functions as hf

if __name__ == "__main__":

    data_folder = "../data"

    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", type=bool, dest="filter")
    parser.add_argument("--filename", type=str, dest="filename")
    args = parser.parse_args()

    space_words = hf.get_text_data(data_folder, "space_words.txt", "|")
    horror_words = hf.get_text_data(data_folder, "horror_words.txt", "|")
    fantasy_words = hf.get_text_data(data_folder, "fantasy_words.txt", "|")
    deny_words = hf.get_text_data(data_folder, "deny_words.txt", "|")
    title_filter_words = hf.get_text_data(data_folder, "title_filter_words.txt", "|")
    # use a few word grouping in filtering plots
    search_words = space_words + fantasy_words + horror_words

    plot_data = hf.get_text_data(data_folder, "generated_text.txt", "\n<|endoftext|>\n")

    clean_plots = hf.clean_plots(plot_data, charlim=True)
    plot_d = hf.get_cleaner_plot_dict(clean_plots, title_filter_words)

    # If plots will be filtered to a list containing keywords, use this function
    if args.filter:
        plot_d = hf.filter_plots(plot_d, search_words, deny_words)

    # Write new files to json
    hf.update_json(data_folder, args.filename, plot_d)
