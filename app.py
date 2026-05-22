from flask import Flask, render_template, request, jsonify
import pickle
import os

app = Flask(__name__)

# Load model and vectorizer
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    model_loaded = True
except FileNotFoundError:
    model_loaded = False
    print("⚠️ Warning: Model files not found. Run train_model.py first!")

@app.route('/')
def index():
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/api/predict', methods=['POST'])
def predict():
    if not model_loaded:
        return jsonify({'error': 'Model not loaded. Run training first.'}), 500
    
    data = request.json
    email_text = data.get('email', '').strip()
    
    if not email_text:
        return jsonify({'error': 'Email text is empty'}), 400
    
    try:
        # Transform and predict
        email_tfidf = vectorizer.transform([email_text])
        prediction = model.predict(email_tfidf)[0]
        confidence = model.predict_proba(email_tfidf)[0]
        
        result = {
            'is_spam': bool(prediction),
            'label': 'SPAM' if prediction == 1 else 'NOT SPAM',
            'confidence': float(max(confidence)) * 100,
            'spam_probability': float(confidence[1]) * 100,
            'legitimate_probability': float(confidence[0]) * 100
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        'model_loaded': model_loaded,
        'model_type': 'Multinomial Naive Bayes',
        'feature_extraction': 'TF-IDF Vectorizer',
        'max_features': 3000
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
