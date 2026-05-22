import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pickle
import os
import urllib.request
import zipfile

print("=" * 60)
print("EMAIL SPAM CLASSIFIER - MODEL TRAINING")
print("=" * 60)

# Download dataset if not exists
dataset_path = "emails.csv"

if not os.path.exists(dataset_path):
    print("\n📥 Downloading spam email dataset...")
    # Using a public spam dataset
    url = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/spam.csv"
    try:
        urllib.request.urlretrieve(url, dataset_path)
        print("✅ Dataset downloaded successfully!")
    except:
        print("⚠️ Could not auto-download. Creating sample dataset...")
        # If download fails, create a minimal sample dataset
        sample_data = {
            'text': [
                "Click here to win free money now!!!",
                "Meeting at 3pm tomorrow",
                "Congratulations you won the lottery",
                "Can you send me the quarterly report",
                "URGENT: Claim your free gift card",
                "Coffee tomorrow at 10am?",
                "You have been selected for a prize",
                "Let's sync up on the project",
                "FREE MONEY FREE MONEY",
                "The project deadline is next Friday"
            ],
            'label': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(dataset_path, index=False)
        print("✅ Sample dataset created!")

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv(dataset_path, sep='\t', names=['label', 'message'])
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# Handle different column names
if 'text' in df.columns and 'label' in df.columns:
    X = df['text']
    y = df['label']
elif len(df.columns) == 2:
    X = df.iloc[:, 1]  # Second column is usually the text
    y = df.iloc[:, 0]  # First column is usually the label
else:
    print("Error: Dataset format not recognized. Expected 'text' and 'label' columns.")
    exit(1)

print(f"Total emails: {len(df)}")
print(f"Spam emails: {(y == 1).sum()}")
print(f"Non-spam emails: {(y == 0).sum()}")

# Split data
print("\n🔀 Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Feature extraction
print("\n🔍 Extracting features with TF-IDF...")
vectorizer = TfidfVectorizer(max_features=3000, stop_words='english', lowercase=True)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"Number of features: {X_train_tfidf.shape[1]}")

# Train model
print("\n🤖 Training Naive Bayes classifier...")
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# Evaluate
print("\n📈 Evaluating model...")
y_pred = model.predict(X_test_tfidf)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\nAccuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"Recall:    {recall:.4f} ({recall*100:.2f}%)")
print(f"F1-Score:  {f1:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"True Negatives:  {cm[0][0]}")
print(f"False Positives: {cm[0][1]}")
print(f"False Negatives: {cm[1][0]}")
print(f"True Positives:  {cm[1][1]}")

# Save model and vectorizer
print("\n💾 Saving model and vectorizer...")
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Model and vectorizer saved!")
print("\n" + "=" * 60)
print("✨ TRAINING COMPLETE - Ready to deploy!")
print("=" * 60)
