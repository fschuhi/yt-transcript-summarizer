# YouTube Transcript Summarizer

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://fschuhi.github.io/yt-transcript-summarizer/)

A tool to summarize YouTube videos using their transcripts.

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file (see Configuration)
4. Run the server: `python main.py`
5. Open `http://127.0.0.1:8000` in your browser

## Features

- Summarize YouTube videos using AI models
- Adjustable summary length
- Support for multiple ChatGPT models
- Web-based user interface

## Configuration

Create a `.env` file in the project root with the following:
```
API_KEY=your_api_key_for_the_summarizer_app
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Usage

1. Enter a YouTube video URL
2. Select desired summary length and AI model
3. Click "Summarize"

Note: Summarization will fail if the video doesn't have captions (CC) available.

## Development

This project uses:
- FastAPI for the backend
- JavaScript for the frontend
- GitHub Pages for documentation

For more details on the project structure, authentication flow, and API dependencies, please refer to the [documentation](https://fschuhi.github.io/yt-transcript-summarizer/).

## Contributing

This is a personal learning project, but suggestions and feedback are welcome. Feel free to open an issue or submit a pull request.

## License

MIT