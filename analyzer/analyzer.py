import os
import time
import logging
from itertools import cycle
from groq import Groq
from ratelimit import limits, sleep_and_retry
from .config import tokens
from typing import List
from requests.exceptions import HTTPError, ConnectionError, Timeout
import functools
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("code_analyzer.log"),
        logging.StreamHandler()
    ]
)

CALLS = 5
PERIOD = 1

def retry(exceptions, tries=3, delay=1, backoff=2):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"{e}, Retrying in {_delay} seconds...")
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)
        return wrapper_retry
    return decorator_retry

class CodeAnalyzer:
    def __init__(self, directory: str, max_retries: int = 5, timeout: float = 20.0):
        self.directory = directory
        self.token_cycle = cycle(tokens)
        self.client = Groq(max_retries=max_retries, timeout=timeout)

    def get_next_token(self) -> str:
        return next(self.token_cycle)

    @sleep_and_retry
    @limits(calls=CALLS, period=PERIOD)
    @retry((HTTPError, ConnectionError, Timeout), tries=3)
    def process_code(self, file_path: str, model_token: str, content: str) -> str:
        try:
            logging.info(f"Processing {file_path} with token {model_token}")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a security code analyzer specialized in static code analysis. Analyze the provided code snippet for vulnerabilities, "
                            "secrets, and code quality issues. For each issue found, provide:\n"
                            "- Severity level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`)\n"
                            "- A brief description of the issue\n"
                            "- The line number where the issue occurs (if available)\n"
                            "If no issues are found, respond with 'SEVERITY: INFO - No significant vulnerabilities detected.'\n"
                            "Provide your response in the following JSON format:\n"
                            "{\n"
                            "  \"issues\": [\n"
                            "    {\n"
                            "      \"severity\": \"<SEVERITY_LEVEL>\",\n"
                            "      \"description\": \"<ISSUE_DESCRIPTION>\",\n"
                            "      \"line\": <LINE_NUMBER>\n"
                            "    },\n"
                            "    ...\n"
                            "  ]\n"
                            "}\n"
                            "Do not include any additional text outside of the JSON format."
                        )
                    },
                    {"role": "user", "content": content},
                ],
                model=model_token,
                temperature=0.1,
                max_tokens=512,
                top_p=1,
                stream=False
            )
            return chat_completion.choices[0].message.content
        except (HTTPError, ConnectionError, Timeout) as e:
            logging.error(f"Network error processing {file_path}: {e}")
            return f"Network error: {e}"
        except Exception as e:
            logging.exception(f"Unhandled exception processing {file_path}")
            return f"Error: {e}"

    def split_content(self, content: str, max_length: int = 5000) -> List[str]:
        return [content[i:i + max_length] for i in range(0, len(content), max_length)]

    def analyze(self, html_report) -> None:
        for root, _, files in os.walk(self.directory):
            for filename in files:
                if filename.endswith((".py", ".js", ".java", ".cpp", ".c", ".cs", ".ts")):
                    file_path = os.path.join(root, filename)
                    current_token = self.get_next_token()
                    logging.info(f"Analyzing file: {file_path}")

                    try:
                        content = self.read_file(file_path)
                    except Exception as e:
                        logging.error(f"Failed to read {file_path}: {e}")
                        continue

                    contents = self.split_content(content) if len(content) > 5000 else [content]

                    summaries = []
                    for content_chunk in contents:
                        start_time = time.time()
                        result = self.process_code(file_path, current_token, content_chunk)
                        try:
                            issues = json.loads(result).get('issues', [])
                        except json.JSONDecodeError:
                            logging.error(f"Failed to parse JSON response for {file_path}")
                            issues = []
                        summaries.extend(issues)

                    # Combine issues from all chunks
                    html_report.add_file_summary(file_path, summaries)

    def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
