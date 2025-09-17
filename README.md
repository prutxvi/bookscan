# BookScan

BookScan is a tool for instant, honest book reviews powered by AI. This project provides a web interface to analyze and summarize book reviews from various sources.

## Features
- Instantly analyze book reviews
- Clean, modern UI
- Powered by AI for accurate summaries

## Getting Started

### 1. Clone the repository

```
git clone https://github.com/prutxvi/bookscan.git
cd bookscan
```

### 2. Set up the environment

- Copy `.env.example` to `.env` and fill in your API keys and settings.
- Create a virtual environment and activate it:

```
python -m venv venv
.\venv\Scripts\Activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

- Install dependencies:

```
pip install -r requirements.txt
```

### 3. Run the app

```
python app.py
```

The app will be available at `http://localhost:5000` (or the port specified in your `.env`).

## Environment Variables
See `.env.example` for required variables.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)
