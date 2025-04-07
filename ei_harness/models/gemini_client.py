import os
from google import genai
from google.genai.types import HttpOptions

def init_client():
    """
    Initialize and return a Gen AI client configured for Vertex AI.
    
    Required environment variables:
      - GOOGLE_CLOUD_PROJECT
      - GOOGLE_CLOUD_LOCATION
    """
    options = HttpOptions(api_version="v1beta1")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not project or not location:
        raise ValueError("Missing GOOGLE_CLOUD_PROJECT and/or GOOGLE_CLOUD_LOCATION environment variables for Vertex AI usage.")
    # Initialize client with Vertex AI settings.
    client = genai.Client(http_options=options, project=project, location=location)
    return client
