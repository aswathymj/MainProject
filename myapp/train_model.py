import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Load Data
df =pd.read_csv('myapp/data.csv')

# Prepare Features and Labels
X = df['Complaint']
y = df['Can Be Solved at Home']

# Build and Train Model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

model.fit(X, y)

# Save Model
joblib.dump(model, 'chatbot_model.pkl')
