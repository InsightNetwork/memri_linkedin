import os

# each page has 100 tweets
PAGE_LIMIT: int = int(os.environ.get("LINKEDIN_PAGE_LIMIT", 2))
# max results per request
MAX_RESULTS: int = int(os.environ.get("LINKEDIN_MAX_RESULTS", 100))

# Used for development, to skip downloading photos
SKIP_PHOTOS: bool = os.environ.get("LINKEDIN_SKIP_PHOTOS", False) in [
    "True",
    "true",
    "1",
]
