# Recursive Subtopics Generator
This project is a Python script that generates a hierarchical structure of subtopics for a given list of topics using GPT-3.5-turbo from OpenAI. It creates subtopic directories in a JSON folder and allows the user to set the maximum depth level for subtopic generation.

## Features

- Generate subtopics for a given list of topics using GPT-3.5-turbo
- Create hierarchical directory structure for subtopics in a JSON folder
- User can set a maximum depth level for subtopic generation

## Use Cases

This project can be used to create a hierarchical structure of topics and subtopics for various purposes, such as:

- Organizing knowledge in a wiki-like format
- Creating a structured database of topics for a content management system
- Developing a content recommendation system based on related topics

## Prerequisites

To use this script, you need an API key for OpenAI's GPT-3.5-turbo. Sign up for an API key [here](https://beta.openai.com/signup/).

## Installation

1. Clone the repository:
git clone https://github.com/mattvlr/recursive-subtopics-generator
2. Install the required dependencies:
pip install -r requirements.txt
3. Set your OpenAI API key as an environment variable:
config.py

## Usage

1. Modify the `main` function in `subtopic_generator.py` to customize the list of topics and the maximum depth level for subtopic generation.

2. Run the script:
python3 main.py
3. The script will create subtopic directories in the `json` folder, organized by the specified topics and subtopics.

4. Explore the generated subtopic hierarchy in the `json` folder.

## License

This project is licensed under the [MIT License](LICENSE).