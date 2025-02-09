import setup_env
from utils import (
    data_extraction,
    data_cleaning,
    data_storage,
    visualization,
    sentiment_analysis,
)
import importlib

# importlib.reload(sentiment_analysis) #use this line of code for modules you need to update to run code in jupyter interactive window, so you do not have to ctrl shift r everytime you make a change and re load the program


# init reddit api
reddit = setup_env.reddit

# extract data
print("Extracting data...\n")
results = data_extraction.extract_data(reddit)
print("Data extracted!\n")

# clean data
print("Cleaning data....")
clean_data = data_cleaning.clean_data(results)
print("Data cleaned!\n")

print("Storing cleaned data... \n")
stored_data = data_storage.store_data(clean_data)
if stored_data:
    print("Data Successfully stored!")
else:
    print("Data Failed to store...")
print("Done storing cleaned data! \n")

# load cleaned data to analyze sentiment
print("Loading clean data...")
cleaned_data = data_storage.load_cleaned_data()
print("Done loading clean data! \n")

# analyze sentiment
print("Analyzing sentiment...")
sentiment_analysis_data = sentiment_analysis.analyze_sentiment(cleaned_data)
print("Done analyzing sentiment!\n")

# store sentiment analysis data
print("Storing sentiment analysis data... \n")
data_storage.store_sentiment_data(sentiment_analysis_data)
print("Done storing sentiment analysis data!")

# visualize results
