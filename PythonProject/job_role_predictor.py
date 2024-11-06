import pickle
import json

class JobRolePredictor:
    def __init__(self):
        with open(r'files/job_role_model.pkl', 'rb') as model_file:
            self.model = pickle.load(model_file)

    def predict(self, job_title):
        title_processed = preprocess_text(job_title)
        return self.model.predict([title_processed])[0]

def preprocess_text(text):
    with open(r"files/stop_words.json", "r") as file:
        stop_words = json.load(file)
    words = text.lower().split()
    words = [word for word in words if word not in stop_words and word != "intern" and word != "internship"]
    return ' '.join(words)
