---
layout: default
title: Requirements
---

# Project Requirements

## Python Dependencies

Below is the current list of Python dependencies for this project:

```{% raw %}

{% include_relative ../requirements.txt %}

```

## Other Requirements

You need to have an OpenAI API key. Create a file .env in the root with the following contents
```
OPENAI_API_KEY=your OpenAI API key
API_KEY=key for the API part of the summarizer app
```
