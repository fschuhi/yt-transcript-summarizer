---
layout: default
title: Requirements
---

# Project Requirements

## Python Dependencies

Below is the current list of Python dependencies for this project:

```
{% include requirements.txt %}
```

## Other Requirements

You need to have an OpenAI API key (see https://openai.com/index/openai-api) and an API key for the YouTube Data API (https://developers.google.com/youtube/v3).

Create a file .env in the root with the following contents
```
API_KEY=key for the API part of the summarizer app
OPENAI_API_KEY=your OpenAI API key
YOUTUBE_API_KEY=your YouTube API key
```
