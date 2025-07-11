"""Configuration module that loads and exposes all environment variables from config.env."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv(Path(__file__).parent / "config.env")

# Project config
PROJECT = os.getenv("PROJECT", "Rosary In A Year (RIAY)")
LOGGING = os.getenv("LOGGING", "false").lower() == "true"
YEAR = int(os.getenv("YEAR", "2025"))

# GitHub config
REPO_OWNER = os.getenv("REPO_OWNER", "linusjf")
REPO_NAME = os.getenv("REPO_NAME", "RIAY")

# Overlay icon config
ICON_FILE = os.getenv("ICON_FILE", "play-button.png")
ICON_SIZE = os.getenv("ICON_SIZE", "256x256")
ICON_OFFSET = os.getenv("ICON_OFFSET", "+32+0")
ICON_COMMENT = os.getenv("ICON_COMMENT", "Play Icon Added")

# Video config
COMPACT_FILE = os.getenv("COMPACT_FILE", "compact.txt")
VIDEOS_FILE = os.getenv("VIDEOS_FILE", "videos.txt")

# CURL config
GAP_BW_REQS = int(os.getenv("GAP_BW_REQS", "0"))
CURL_MAX_RETRIES = int(os.getenv("CURL_MAX_RETRIES", "5"))
CURL_INITIAL_RETRY_DELAY = int(os.getenv("CURL_INITIAL_RETRY_DELAY", "2"))
CURL_CONNECT_TIMEOUT = int(os.getenv("CURL_CONNECT_TIMEOUT", "30"))
CURL_MAX_TIME = int(os.getenv("CURL_MAX_TIME", "90"))

# Transcription config
TRANSCRIBE_VIDEOS = os.getenv("TRANSCRIBE_VIDEOS", "false").lower() == "true"
TRANSCRIBE_LOCALLY = os.getenv("TRANSCRIBE_LOCALLY", "false").lower() == "true"
USE_FASTER_WHISPER = os.getenv("USE_FASTER_WHISPER", "true").lower() == "true"
ENABLE_FAILOVER_MODE = os.getenv("ENABLE_FAILOVER_MODE", "true").lower() == "true"

# ASR config
ASR_LLM_API_KEY = os.getenv("ASR_LLM_API_KEY", "")
ASR_LLM_BASE_URL = os.getenv("ASR_LLM_BASE_URL", "https://api.deepinfra.com/v1")
ASR_LLM_ENDPOINT = os.getenv("ASR_LLM_ENDPOINT", "/openai/audio/transcriptions")
ASR_LLM_MODEL = os.getenv("ASR_LLM_MODEL", "openai/whisper-large-v3")
ASR_LOCAL_MODEL = os.getenv("ASR_LOCAL_MODEL", "small")
ASR_INITIAL_PROMPT = os.getenv("ASR_INITIAL_PROMPT", "In Ascension Press' Rosary in a Year podcast...")
ASR_CARRY_INITIAL_PROMPT = os.getenv("ASR_CARRY_INITIAL_PROMPT", "true").lower() == "true"
ASR_BEAM_SIZE = int(os.getenv("ASR_BEAM_SIZE", "5"))

# YouTube config
YT_DLP_RETRIES = int(os.getenv("YT_DLP_RETRIES", "20"))
YT_DLP_SOCKET_TIMEOUT = int(os.getenv("YT_DLP_SOCKET_TIMEOUT", "30"))
CAPTIONS_OUTPUT_DIR = os.getenv("CAPTIONS_OUTPUT_DIR", "captions")

# AI config
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
TEXT_LLM_API_KEY = os.getenv("TEXT_LLM_API_KEY", "")
TEXT_LLM_BASE_URL = os.getenv("TEXT_LLM_BASE_URL", "https://api.deepseek.com")
TEXT_LLM_CHAT_ENDPOINT = os.getenv("TEXT_LLM_CHAT_ENDPOINT", "/chat/completions")
TEXT_LLM_MODEL = os.getenv("TEXT_LLM_MODEL", "deepseek-chat")

# Prompt templates
SYSTEM_SUMMARY_PROMPT = os.getenv("SYSTEM_SUMMARY_PROMPT", "You are a helpful assistant...")
CHUNK_SUMMARY_PROMPT = os.getenv("CHUNK_SUMMARY_PROMPT", "Summarize this text...")
FINAL_SUMMARY_PROMPT = os.getenv("FINAL_SUMMARY_PROMPT", "Summarize the following text...")
SUMMARY_IMAGE_META_PROMPT = os.getenv("SUMMARY_IMAGE_META_PROMPT", 'You are an assistant...')
SUMMARY_ARTWORK_DETAILS_PROMPT = os.getenv("SUMMARY_ARTWORK_DETAILS_PROMPT", "From the following text...")

# Image generation config
AUTO_GENERATE_IMAGES = os.getenv("AUTO_GENERATE_IMAGES", "false").lower() == "true"
IMAGE_GENERATION_SCRIPT = os.getenv("IMAGE_GENERATION_SCRIPT", "openaigenerateimage")
DEEPINFRA_IMAGE_GENERATION_MODEL = os.getenv("DEEPINFRA_IMAGE_GENERATION_MODEL", "stabilityai/sd3.5")
FALAI_IMAGE_GENERATION_MODEL = os.getenv("FALAI_IMAGE_GENERATION_MODEL", "janus")

# Art downloader config
ART_DOWNLOADER_DIR = os.getenv("ART_DOWNLOADER_DIR", "artdownloads")
VERIFY_ART_IMAGES = os.getenv("VERIFY_ART_IMAGES", "false").lower() == "true"
ART_METADATA_PROMPT = os.getenv("ART_METADATA_PROMPT", "You are an expert on Christian art...")
IMAGE_CONTENT_VALIDATION = os.getenv("IMAGE_CONTENT_VALIDATION", "lenient")
VECTOR_EMBEDDINGS_MODEL_API_KEY = os.getenv("VECTOR_EMBEDDINGS_MODEL_API_KEY", "")
VECTOR_EMBEDDINGS_BASE_URL = os.getenv("VECTOR_EMBEDDINGS_BASE_URL", "https://api.deepinfra.com/v1/openai")
VECTOR_EMBEDDINGS_MODEL = os.getenv("VECTOR_EMBEDDINGS_MODEL", "thenlper/gte-large")

# Stock photo sites (loaded as list)
STOCK_PHOTO_SITES = [
    "alamy.com",
    "gettyimages.com",
    "gettyimages.co.uk",
    "istockphoto.com",
    "shutterstock.com",
    "dreamstime.com",
    "123rf.com",
    "depositphotos.com",
    "fineartamerica.com",
    "pixels.com",
    "bigstockphoto.com",
    "fotolia.com",
    "stock.adobe.com",
    "canstockphoto.com",
    "picfair.com",
    "granger.com",
    "bridgemanimages.com",
    "agefotostock.com",
    "europosters.nl",
    "nikkel-art.be",
    "etsy.com",
    "pixers.us",
    "ebayimg.com"
]
