#!/usr/bin/env python

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load tokenizer and model from Hugging Face
model_name = "google/gemma-3-270m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create a text generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Generate text from a prompt
prompt = "The 10 meter ham radio band allows for many different modes of operation"
output = generator(prompt, max_length=100, do_sample=True, temperature=0.7)

# Print the generated text
print(output[0]["generated_text"])

