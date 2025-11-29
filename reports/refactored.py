import os

def crash_me(data):
    key = os.environ.get("API_KEY")
    return data[0]