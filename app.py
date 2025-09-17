from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq
from goodreads_scraper import fetch_goodreads_reviews
import re
import json

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/scan')
def scan_page():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    book_title = request.json.get('book_title', '').strip()
    reviews = fetch_goodreads_reviews(book_title)
    if not reviews:
        return jsonify({
            'book_title': book_title,
            'purpose': 'No information found.',
            'verdict': '',
            'star_rating': 0,
            'star_label': 'No rating',
            'likes': [],
            'dislikes': [],
            'best_for': [],
            'avoid_if': [],
            'tags': [],
            'analysis': 'No reviews found or book not found.'
        })

    prompt = f"""
You are an expert, honest book reviewer. Analyze the following real reader reviews of "{book_title}" and return a concise, structured JSON:
- book_title (string)
- purpose (string, 1-sentence summary of the book's main aim)
- verdict (string, your truthfully enthusiastic or cautious recommendation, as in a YouTube review)
- star_rating (integer 1-20: rate the book for intended audience, no fractions)
- star_label (string: Must-read / Worth your time / Middling / Only for fans / Skip it)
- likes (list, up to 5 punchy bullets)
- dislikes (list, up to 5 punchy bullets)
- best_for (list, 1-3 ideal audience types)
- avoid_if (list, 1-3 types who probably won't like it)
- tags (list: writing level, practicality, scientific rigor)
- analysis (fallback prose summary paragraph)
Return only valid JSON.

Here are live user reviews:
{chr(10).join(reviews)}
    """

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )

    output = completion.choices[0].message.content
    try:
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found.")
        # Defensive: ensure all keys present and correct
        keys = ["book_title","purpose","verdict","star_rating","star_label",
                "likes","dislikes","best_for","avoid_if","tags","analysis"]
        for key in keys:
            if key not in data: data[key] = [] if key in ["likes","dislikes","best_for","avoid_if","tags"] else ""

        # Guarantee types
        for field in ["likes","dislikes","best_for","avoid_if","tags"]:
            if not isinstance(data[field], list): data[field] = []
        try: data["star_rating"] = int(data.get("star_rating", 0))
        except: data["star_rating"] = 0
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'book_title': book_title,
            'purpose': '',
            'verdict': '',
            'star_rating': 0,
            'star_label': '',
            'likes': [],
            'dislikes': [],
            'best_for': [],
            'avoid_if': [],
            'tags': [],
            'analysis': output[:1500],
        })

if __name__ == '__main__':
    app.run(debug=True)
