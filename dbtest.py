from pymongo import MongoClient
from fuzzywuzzy import process, fuzz

#connecting to mongodb 
client = MongoClient("mongodb://localhost:27017/")
db = client.test_cb
collection = db.test_collection

#data to be inserted
data = [
    {"question": "What is a binary search?", "answer": "Binary search is a search algorithm that finds the position of a target value within a sorted array."},
    {"question": "Explain quicksort.", "answer": "Quicksort is a divide-and-conquer algorithm that sorts an array."}
]

#inserts data to db
collection.insert_many(data)

#fetching answers from db
def fetch_answer(question):
    #fetching all question
    all_questions = list(collection.find({}, {"question": 1, "answer": 1}))
    
    question_list = [q["question"] for q in all_questions]
    
    #using fuzzy match to find the closest question
    closest_match = process.extractOne(question, question_list, scorer=fuzz.ratio)
    
    if closest_match and closest_match[1] > 70: 
        matched_question = closest_match[0]
        for q in all_questions:
            if q["question"] == matched_question:
                return q["answer"]
    
    return "Sorry, I couldn't find an answer to that question."

user_question = "What is a binary search?"
response = fetch_answer(user_question)
print(response)
