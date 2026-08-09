import os

API_KEY = os.getenv("OPENROUTER_API_KEY")
COMMON_FREE_MODELS = ["nvidia/nemotron-3-ultra-550b-a55b:free", "poolside/laguna-s-2.1:free"]
DEFAULT_MODEL = COMMON_FREE_MODELS[0]