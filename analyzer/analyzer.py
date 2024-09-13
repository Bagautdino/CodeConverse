import os
import time
import logging
from itertools import cycle
from groq import Groq
from .config import tokens

class CodeAnalyzer:
    def __init__(self, directory, max_retries=5, timeout=20.0):
        self.directory = directory
        self.token_cycle = cycle(tokens)
        self.client = Groq(max_retries=max_retries, timeout=timeout)

    def get_next_token(self):
        return next(self.token_cycle)

    def process_code(self, file_path, model_token, content):
        try:
            logging.info(f"Processing {file_path} with token {model_token}")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "Start your response with a severity level ('SEVERITY: CRITICAL' or 'SEVERITY: HIGH') and briefly summarize key vulnerabilities and secrets in the code in one sentence."},
                    {"role": "user", "content": content},
                ],
                model=model_token,
                temperature=0.1,
                max_tokens=512,
                top_p=1,
                stream=False
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            return str(e)

    def split_content(self, content, max_length=5000):
        return [content[i:i + max_length] for i in range(0, len(content), max_length)]

    def analyze(self, html_report):
        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                if filename.endswith((".py", ".js", ".java", ".cpp", ".c", ".cs", ".ts")):
                    file_path = os.path.join(root, filename)
                    current_token = self.get_next_token()
                    logging.info(f"Analyzing file: {file_path}")

                    try:
                        with open(file_path, 'r', errors='ignore') as file:
                            content = file.read()
                    except Exception as e:
                        logging.error(f"Failed to read {file_path}: {e}")
                        continue

                    if len(content) > 5000:
                        contents = self.split_content(content)
                    else:
                        contents = [content]

                    summaries = []
                    for content_chunk in contents:
                        start_time = time.time()
                        result = self.process_code(file_path, current_token, content_chunk)
                        summaries.append(result)
                        request_interval = time.time() - start_time
                        time.sleep(max(0, request_interval - (time.time() - start_time)))

                    summary = "\n".join(summaries)
                    logging.info(f"Summary for {file_path}: {summary}")
                    logging.info("-" * 60)

                    html_report.add_file_summary(file_path, summary)
