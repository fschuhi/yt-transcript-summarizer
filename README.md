# YouTube Transcript Summarizer

## Description
Does what it says: summarize a YT video, using the video's transcript.

## Installation
- See _run.bat_ for how to start the server.
- Server listens on 127.0.0.1:8000.

## Usage
- The UI is self-explanatory. Just specify which video to summarize and select summary length and model.
- **IMPORTANT**: You need an .env in the project root, containing your OpenAI API key.
- Note that summarize will fail if the video doesn't have captions (CC turned off).

## Features
- Only a few ChatGPT models are available. You would usually use the GPT 4o mini.
- The code tries to instruct ChatGPT to create a summary which length should be  close to what you asked it. It can vary, though.  

## Dependencies
- youtube_transcript_api
- openai
- python-dotenv
- fastapi
- uvicorn
- jinja2
- python-multipart
- pydantic
- colorama
- starlette

## License
MIT