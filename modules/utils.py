from datetime import datetime


def get_today():
    return datetime.now().strftime("%B %d, %Y")


def shorten_title(prompt, max_len=30):
    return prompt[:max_len] + ("..." if len(prompt) > max_len else "")
