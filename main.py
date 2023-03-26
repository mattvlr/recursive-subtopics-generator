# main.py

import openai
import json
import os
import time
from config import API_KEY

openai.api_key = API_KEY

def get_subtopics_recursive(topic, parent_path, level=1, max_level=4):
    start_time = time.time()
    if level > max_level:
        return

    process_status = f"""
    Processing
    Topic: {topic}
    Parent path: {parent_path}
    Level: {level}
    Max level: {max_level}
    """
    print(process_status)

    prompt = f"""
    Given a topic, return a json object of subtopics for the topic. Name one and only object "subtopics".
    Parent topic location: {parent_path}
    Topic: {topic}"""
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as e:
        print("Error:", e)
        return

    answer_short = completion.choices[0].message
    answer_text_short = answer_short['content']

    try:
        json_obj = json.loads(answer_text_short)
        subtopics = json_obj.get("subtopics")

        for subtopic in subtopics:
            subtopic_dir = os.path.join(parent_path, subtopic)
            os.makedirs(subtopic_dir, exist_ok=True)
            get_subtopics_recursive(subtopic, subtopic_dir, level=level + 1, max_level=max_level)

    except Exception as e:
        print("Error decoding JSON:", e)
        return

    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken for level {level}: {time_taken:.2f} seconds")


def main():
    # List of topics to generate subtopics for
    topics = [
        "Agriculture", "Anthropology", "Architecture", "Art", "Astronomy", "Automotive industry", "Aviation", "Biology", "Business", "Chemistry", "Communications", "Computer science", "Construction", "Culture", "Defense", "Demographics", "Ecology", "Education", "Energy", "Engineering", "Environment", "Ethics", "Film", "Finance", "Food and nutrition", "Forestry", "Geography", "Geology", "Government", "Health", "History", "Industry", "Information science", "Journalism", "Law", "Languages", "Linguistics", "Literature", "Mathematics", "Media studies", "Medicine", "Military", "Music", "Mythology", "Natural disasters", "Other", "Philosophy", "Physics", "Politics", "Psychology", "Religion", "Science", "Sociology", "Sports", "Technology", "Telecommunications", "Transportation", "Travel"
    ]

    # Set the maximum depth for subtopic generation (default is 4)
    # Increasing max_level will generate deeper subtopic hierarchies, but it will take more time to process
    max_level = 4

    # Create the 'json' directory if it doesn't exist
    # This ensures that the script has a place to store the generated subtopic hierarchies
    os.makedirs('./json/', exist_ok=True)
    
    # Iterate through each topic in the list
    for topic in topics:
        # Record the start time to calculate the time taken for processing each topic
        start_time = time.time()

        # Create a directory for the current topic inside the 'json' directory
        topic_dir = f"./json/{topic}"
        os.makedirs(topic_dir, exist_ok=True)

        # Generate subtopics for the current topic and save them in the corresponding directory
        get_subtopics_recursive(topic, topic_dir, max_level=max_level)

        # Calculate and display the time taken for processing the current topic
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Time taken for topic {topic}: {time_taken:.2f} seconds")

if __name__ == "__main__":
    main()