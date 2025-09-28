#!/usr/bin/env python

#
# Simple Hugging Face example using Gemma model for text generation
#

import os
import argparse
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate text using Gemma model.')
    parser.add_argument('prompt', type=str, help='Input prompt for text generation')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("HF_TOKEN")

    # Initialize the model and tokenizer
    model_name = "google/gemma-3-270m"  # Using the 270M parameter version
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Create a text generation pipeline
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=100,  # Adjust the max length of generated text as needed
        temperature=0.7  # Adjust temperature for creativity (higher = more creative)
    )
    
    # Generate text based on the input prompt
    result = generator(args.prompt)
    print("\nGenerated text:")
    print(result[0]['generated_text'])

if __name__ == "__main__":
    main()