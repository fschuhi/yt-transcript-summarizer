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

The requirements specifically for development purporses are:

```
{% include requirements-dev.txt %}
```

## Other Requirements

Environment variables are supplied by `.env`. As a template, here is `.env.example` which shows the necessary values to supply to the application.

```
{% include .env.example %}
```
