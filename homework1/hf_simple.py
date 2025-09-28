#!/usr/bin/env python

#
# Simple Hugging Face example using sentiment-analysis model to test API access
#

import os
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

api_key = os.getenv("HF_TOKEN")

sentiment_pipeline = pipeline("sentiment-analysis")

result = sentiment_pipeline("I love using Hugging Face Transformers!")

print(result)
