# CS 330 Homework 1 : Getting Started

The goal of this assignment is to set up an AI-powered development environment and begin the process of final-project planning.

## Development Environment

Lenovo T440p laptop

* Intel(R) Core(TM) i5-4300M CPU @ 2.60GHz
* 8GB RAM
* Debian 12
* Python 3.11
* Visual Studio Code & Vim for editing
* Sqlite3 and PostgreSQL for databases

## AI Agent

Todo

## Python and Test Models

Activate python virtual environment 

```
source ~/cs330_venv/bin/activate
```

### Sentiment-analysis / Gemma Models

1. Created Hugging Face Account
2. Accept Gemma License Agreement
3. Model [description](https://huggingface.co/google/gemma-3-270m) on site.
4. Can be used via libraries (transformers), notebooks, or local apps.
5. Created Hugging Face Access token (read) stored in .env file.
6. Created basic script to verify model connectivity.
7. Script does not run, need to create python venv on Debian 12 and pip install transformers and torch (lots of dependencies). 
8. Todo: Verify it runs in vscode as well.
9. Had Claude Sonnet add ability to specify text on command line.
10. Saved a chat transcript in a Markdown file.
11. Gave the small Gemma model a bunch of prompts. Need to adjust how it is called? Seems to generate repetitive output.

### Example Program Output
<pre>
(cs330_venv) steve@kitsap:~/GITHUB/cs330-projects/homework1$ ./hf_simple.py 
No model was supplied, defaulted to distilbert/distilbert-base-uncased-finetuned-sst-2-english and revision 714eb0f (https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).
Using a pipeline without specifying a model name and revision in production is not recommended.
config.json: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 629/629 [00:00<00:00, 2.54MB/s]
model.safetensors: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 268M/268M [00:24<00:00, 10.9MB/s]
tokenizer_config.json: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 48.0/48.0 [00:00<00:00, 226kB/s]
vocab.txt: 232kB [00:00, 6.14MB/s]
Device set to use cpu
[{'label': 'POSITIVE', 'score': 0.9971315860748291}]
</pre>

<pre>
(cs330_venv) steve@kitsap:~/GITHUB/cs330-projects/homework1$ ./hf_simple.py "I think this ham radio antenna is mediocre at best"
No model was supplied, defaulted to distilbert/distilbert-base-uncased-finetuned-sst-2-english and revision 714eb0f (https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).
Using a pipeline without specifying a model name and revision in production is not recommended.
Device set to use cpu
[{'label': 'NEGATIVE', 'score': 0.9997625946998596}]
</pre>

<pre>
(cs330_venv) steve@kitsap:~/GITHUB/cs330-projects/homework1$ ./gemma_simple.py "write a horoscope for capricorn"
Device set to use cpu

Generated text:
write a horoscope for capricorn
Capricorn has a unique way of thinking. He is a very logical and analytical man. He is very good at making decisions and taking the right decisions. He is very good at thinking out a plan. He is very good at making decisions and taking the right decisions. He is very good at making decisions and taking the right decisions. He is very good at making decisions and taking the right decisions.He is a very good at making decisions and taking the
</pre>

### Steve's Notes

Calling a language model has two steps: tokenizing and inference.

Models can't operate on words, so the tokenizer converts text into a list of numbers. A token is either a word or a part of a word.

Inference can then be performed on this list (vector) of numbers.

1. Select Test Data Set

## Database Setup

1. Sqlite test
2. Postgresql test

## Project Planning 

My favorite hobby is ham radio. I would like to develop an AI model to predict worldwide high frequency (HF) radio propagation. 
Traditional HF propagation programs have relied on solar data for their predictions. For example, the popular W6ELprop program
uses something called the Solar Terrestrial Dispatch (STL) model. I would like to take a difference approach based on the observation
that certain propagation trends tend to persist for a period of time. It is not guaranteed that propagation at 28 Mhz will be good tomorrow
because it was good today, but it probably will. I think these types of probabilistic radio phenomena may be well-suited to prediction
by a machine learning model. I would like to explore this possibiliy in my project.

## Data Set

Solar data is plentiful and publicly available. I definitely want to keep it in mind, but for now I think I would like to focus on data that
is in general referred to as DX spots. The DX (or distance) spots are human-created or automated reports of radio transmissions that are received
by a listening station, along with information about their origin. Regardless of how the data are created in a reporting system, the result is
that an arc connecting two points on the globe can be determined such that a radio wave propagation path is identified between the two points.
Additional information such as signal strength may be included in the reports as well. These reports are collected by various networks or 
dedicated web sites for the purpose of providing real-time reporting of conditions and stations operating. I would like to collect some of 
this data and use it to make predictions about future propagation conditions for the coming days or weeks. 

### Data Sources

* DX Clusters
* DXmaps.com
* Reverse Beacon Network
* Others...

### Running the data collector script

<pre>
jersey% nohup ./dx-cluster.py &
[1] 1169999
jersey% nohup: ignoring input and appending output to 'nohup.out'
</pre>
