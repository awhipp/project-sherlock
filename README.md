# Project Sherlock

Project which allows users to scrape website information and then use generative AI to allow users to ask questions about all the data.

## Architecture (WIP)

* Web Scraper
**Python 3.11
**FastAPI (Python web framework)
**Pydantic (Python data validation)

* Query Interface
**[Open Web UI](https://docs.openwebui.com/)
**[Ollama](https://ollama.com/)

## How to use

### Start up Open Web UI and Ollama

```bash
docker-compose up -d
```

### Register and Login

* URL: http://localhost:3000
* First registration gets admin access.

### Settings / Models / Documents Setup

* User > Settings > General > Advanced Settings
**Tweak these accordingly based on desired performance
* User > Settings > Models
**Download a Model (i.e. `llama3:latest`)
* User > Settings > Images
**Add Image Generation Base URL (!TODO)
* Documents > Document Settings
**Embedding Model Engine: Ollama (or your choice)
**Chunk Params > PDF Extract Images > On


## Docker Commands

Open Web UI

```bash
docker logs open-webui
```

Ollama

```bash
docker logs ollama
```

Exec into Open Web UI

```bash
docker exec -it open-webui /bin/bash
```
