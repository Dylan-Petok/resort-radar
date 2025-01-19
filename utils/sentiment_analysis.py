from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd
import numpy as np
from utils import data_storage
from sqlalchemy import create_engine


# Define label mappings
label_mapping = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# Load model and tokenizer for Cardiff NLP's RoBERTa sentiment analysis
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def analyze_sentiment(data: pd.DataFrame) -> pd.DataFrame:
    """
    Perform sentiment analysis on a DataFrame of text, handling posts longer than 512 tokens by splitting
    and averaging sentiment scores.

    Args:
        data (pd.DataFrame): The input DataFrame containing a 'P_TEXT' column with text to analyze.

    Returns:
        pd.DataFrame: The input DataFrame with added 'sentiment_label' and 'sentiment_score' columns.
    """
    def process_post(text):
        if not text or not text.strip():  # Check if the text is empty or just whitespace
            return "Neutral", 0.0  # Default sentiment for empty texts

        # Tokenize the text without truncation
        tokens = tokenizer(text, truncation=False, return_tensors="pt")["input_ids"][0]
        if len(tokens) == 0:  # Check if tokenization resulted in no tokens
            return "Neutral", 0.0

        # Split tokens into chunks of 512
        token_chunks = [tokens[i:i + 512] for i in range(0, len(tokens), 512)]
        chunk_scores = []

        # Analyze each chunk
        for chunk in token_chunks:
            chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
            try:
                result = sentiment_pipeline(chunk_text)[0]  # Analyze sentiment
                chunk_scores.append(result)
            except Exception as e:
                print(f"Error analyzing chunk: {e}")
                continue

        if len(chunk_scores) == 0:  # Handle cases where no valid chunks were analyzed
            return "Neutral", 0.0

        # Average the scores and determine the final sentiment
        avg_score = np.mean([score['score'] for score in chunk_scores])
        avg_label_raw = max(chunk_scores, key=lambda x: x['score'])['label']  # Most confident label
        avg_label = label_mapping[avg_label_raw]  # Map to human-readable label


        return avg_label, avg_score


    # Analyze each post in the DataFrame
    results = data['P_TEXT'].apply(process_post)
    data['sentiment_label'] = results.apply(lambda x: x[0])
    data['sentiment_score'] = results.apply(lambda x: x[1])

    print('Done analyzing sentiment!')
    return data