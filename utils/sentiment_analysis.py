# pylint: disable=E1137
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd


# Define label mappings
label_mapping = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}

# Load model and tokenizer for Cardiff NLP's RoBERTa sentiment analysis
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def analyze_sentiment(data: pd.DataFrame) -> pd.DataFrame:
    """
    Perform sentiment analysis on each post in the DataFrame by splitting long posts into chunks,
    obtaining the full probability distributions for each chunk, and then aggregating these distributions
    (weighted by chunk length) to produce an overall sentiment.

    The final sentiment label is determined by the maximum probability in the aggregated distribution,
    and the corresponding probability is used as the sentiment score.
    """

    def process_post(text):
        if not text or not text.strip():  # Check for empty or whitespace-only text
            return "Neutral", 0.0

        # Tokenize the text without truncation
        tokens = tokenizer(text, truncation=False, return_tensors="pt")["input_ids"][0]
        if len(tokens) == 0:
            return "Neutral", 0.0

        # Determine the maximum allowed sequence length from the model configuration.
        # For example, model.config.max_position_embeddings might be 514.
        max_length = model.config.max_position_embeddings

        # Determine how many special tokens are added by the tokenizer.
        special_tokens_count = len(tokenizer.build_inputs_with_special_tokens([]))

        # Add a safety margin to ensure that when the text is re-tokenized (with special tokens added),
        # it doesn't exceed the model's allowed length.
        safety_margin = 2
        chunk_size = max_length - special_tokens_count - safety_margin

        # Split tokens into chunks of the calculated chunk_size
        token_chunks = [
            tokens[i : i + chunk_size] for i in range(0, len(tokens), chunk_size)
        ]

        aggregated_probs = None  # To accumulate weighted probabilities
        total_tokens = 0

        for idx, chunk in enumerate(token_chunks):
            # Decode the chunk to text. We skip special tokens since they will be added later.
            chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
            try:
                # Enable truncation so that re-tokenized text does not exceed the model's max length.
                results = sentiment_pipeline(chunk_text, truncation=True, top_k=None)
                # print(results)
                # print(f"DEBUG: results type: {type(results)} for chunk {idx}")
                if not results:
                    print(
                        f"Warning: No results returned for chunk {idx} (first 100 chars: {chunk_text[:100]})"
                    )
                    continue

                # Convert list of dicts to a dictionary mapping label to probability
                chunk_probs = {item["label"]: item["score"] for item in results}

                # Weight by the number of tokens in the original chunk
                chunk_length = len(chunk)
                total_tokens += chunk_length

                if aggregated_probs is None:
                    aggregated_probs = {
                        label: prob * chunk_length
                        for label, prob in chunk_probs.items()
                    }
                else:
                    for label, prob in chunk_probs.items():
                        aggregated_probs[label] += prob * chunk_length

            except Exception as e:
                print(f"Error analyzing chunk {idx}: {e}")
                print(f"  Chunk text (first 100 chars): {chunk_text[:100]}")
                print(f"  Chunk length: {len(chunk)} tokens")
                continue

        if aggregated_probs is None:
            return "Neutral", 0.0

        # Compute the average probabilities by dividing by the total token count
        averaged_probs = {
            label: weighted_prob / total_tokens
            for label, weighted_prob in aggregated_probs.items()
        }

        # Select the label with the highest average probability
        overall_label_raw = max(averaged_probs, key=averaged_probs.get)
        overall_score = averaged_probs[overall_label_raw]
        overall_label = label_mapping[overall_label_raw]
        return overall_label, overall_score

    # Apply the process_post function to each text in the DataFrame
    results = data["P_TEXT"].apply(process_post)
    data["sentiment_label"] = results.apply(lambda x: x[0])
    data["sentiment_score"] = results.apply(lambda x: x[1])

    print("Done analyzing sentiment with probability aggregation!")
    return data


# Example usage:
# df = pd.DataFrame({"P_TEXT": ["I love this!", "I hate that...", "It is okay."]})
# df = analyze_sentiment(df)
# print(df)
