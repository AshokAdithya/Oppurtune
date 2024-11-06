import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import nltk
from nltk.corpus import stopwords
import pickle


# Download stopwords if not already downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Load data
data_file = 'augmented_classified_jobs_no_new_roles.csv'
df = pd.read_csv(data_file, encoding='ISO-8859-1')

# Rename columns for clarity
df.rename(columns={'Job Title': 'Job Title', 'Role': 'Job Role'}, inplace=True)

print(df.head())

# Preprocess text function
def preprocess_text(text):
    # Convert to lowercase and split into words
    words = text.lower().split()
    
    # Remove stopwords and specific keywords
    words = [word for word in words if word not in stop_words and word != "intern" and word != "internship"]
    return ' '.join(words)

# Apply preprocessing to job titles
df['Job Title'] = df['Job Title'].apply(preprocess_text)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(df['Job Title'], df['Job Role'], test_size=0.2, random_state=45)

# Create a pipeline with TfidfVectorizer and RandomForestClassifier
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000)),  # Limit to 5000 features
    ('clf', RandomForestClassifier(class_weight='balanced'))  # Using Random Forest with class weighting
])

# Fit the model
pipeline.fit(X_train, y_train)

# Make predictions
y_pred = pipeline.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

#intial configuration for job files
# with open(r"files/ml_jobs.json","r") as file:
#     content=json.load(file)

# for item in content:
#     if item!={}:
#         title_processed=preprocess_text(item["jobTitle"])
#         job_role=pipeline.predict([title_processed])
#         item["jobRole"]=job_role[0]

# with open(r"files/ml_jobs.json","w") as file:
#     json.dump(list(content),file)

with open(r'files/job_role_model.pkl', 'wb') as model_file:
    pickle.dump(pipeline, model_file)
