from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import pandas as pd
import re
from pymongo import MongoClient
from fuzzywuzzy import process, fuzz

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.chatter_db
collection = db.test_collection

# Function to clean data
def clean_data(data):
    data = re.sub(r'[^\s\w,]', '', data)
    data = data.lower().strip()
    return data

# Function to upload data to MongoDB
def upload_data(convo_df):
    conversations = []
    for _, row in convo_df.iterrows():
        question = clean_data(row['question'])
        answer = clean_data(row['answer'])
        if question and answer:
            conversations.append({"question": question, "answer": answer})
    # Upload data to MongoDB
    collection.insert_many(conversations)

# Uncomment this section to upload data from CSV to MongoDB
# file_path = r'tech_questions.csv'
# convo_df = pd.read_csv(file_path)
# upload_data(convo_df)

# Initialize chatbot
chatbot = ChatBot("Chatter")

# Training the chatbot
list_trainer = ListTrainer(chatbot)

# Function to fetch answer from MongoDB
def fetch_answer(question):
    # Fetch all questions from MongoDB
    all_questions = list(collection.find({}, {"question": 1, "answer": 1}))
    
    question_list = [q["question"] for q in all_questions]
    
    # Use fuzzy matching to find the closest question
    closest_match = process.extractOne(question, question_list, scorer=fuzz.token_sort_ratio)
    
    if closest_match and closest_match[1] > 85: 
        matched_question = closest_match[0]
        for q in all_questions:
            if q["question"] == matched_question:
                return q["answer"]
    
    return 0

# Define some extra data (introductory greetings)
basic_greetings = [
    ["Hi", "Hello"],
    ["who are you?", "I am Chatter, here to help you with technology-related questions."],
    ["how are you?", "I am good! How can I assist you with technology today?"]
]

# Train chatbot with basic greetings
for pair in basic_greetings:
    list_trainer.train(pair)

# Train chatbot with inbuilt corpus datasets
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train(
    "chatterbot.corpus.english.ai",
    "chatterbot.corpus.english.computers",
    "chatterbot.corpus.english.science"
)

# Define exit conditions for the chatbot
exit_condition = ("exit", "stop", "quit", ":q", "bye")

# Main loop to interact with the chatbot
while True:
    query = input("\U0001F47D > ")
    if query.lower() in exit_condition:
        break
    else:
        response = fetch_answer(query)
        if response == 0:
            response = chatbot.get_response(query)
        print(f"\U0001F916 {response}")
