Recursive Subtopics Generator
This project uses the OpenAI GPT-3.5-turbo API to generate a hierarchical structure of subtopics for a list of given topics. The generated subtopics are organized into folders to provide an easy-to-understand structure.

Features
Recursively generates subtopics for given topics
Creates a directory structure to represent the hierarchy of subtopics
Customizable depth for subtopic generation
Utilizes the OpenAI GPT-3.5-turbo API for subtopic generation
Prerequisites
Python 3.6 or higher
An OpenAI API key
Dependencies
openai - Install using pip install openai
Setup
Clone the repository:
bash
Copy code
git clone https://github.com/your_username/recursive-subtopics-generator.git
Enter the project directory:
bash
Copy code
cd recursive-subtopics-generator
Install the required dependencies:
Copy code
pip install -r requirements.txt
Create a config.py file in the project root directory with the following content:
python
Copy code
# config.py

API_KEY = "your_openai_api_key_here"
Replace your_openai_api_key_here with your actual OpenAI API key.

Usage
Modify the main() function in main.py to include the topics you'd like to generate subtopics for:
python
Copy code
topics = [
    "Medicine", "Military", "Music", "Mythology", "Natural disasters", "Other", "Philosophy", "Physics", "Politics", "Psychology", "Religion", "Science", "Sociology", "Sports", "Technology", "Telecommunications", "Transportation", "Travel"
]
Run the script:
css
Copy code
python main.py
The generated subtopics will be organized into folders under the ./json/ directory.
Use Cases
Content creators can use this tool to generate a structured set of subtopics for their main topics. This can help them plan and organize their content more efficiently.
Educators can use the generated hierarchy of subtopics to create lesson plans and course outlines.
Researchers can use the subtopics as a starting point for exploring a specific topic in depth.
License
This project is licensed under the MIT License. See the LICENSE file for more information.