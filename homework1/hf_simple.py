#!/usr/bin/env python

#
# Simple Hugging Face example using sentiment-analysis model to test API access
#

import os
import argparse
from dotenv import load_dotenv
from transformers import pipeline

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze sentiment of input text using Hugging Face.')
    parser.add_argument('text', type=str, help='Text to analyze for sentiment')
    args = parser.parse_args()

    # Load environment variables and set up the pipeline
    load_dotenv()
    api_key = os.getenv("HF_TOKEN")
    sentiment_pipeline = pipeline("sentiment-analysis")

    # Analyze the provided text
    result = sentiment_pipeline(args.text)
    print(result)

if __name__ == "__main__":
    main()
