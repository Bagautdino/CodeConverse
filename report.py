import logging
from config import GROQ_API_KEY

class HTMLReport:
    def __init__(self, output_file):
        self.output_file = output_file
        self.report_content = ""

    def start_report(self):
        # Начало HTML отчета
        self.report_content += """
        <html>
        <head>
            <title>Code Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; }
                table, th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
        <h1>Code Analysis Report</h1>
        <table>
        <tr><th>File</th><th>Summary</th></tr>
        """

    def add_file_summary(self, file_path, summary):
        # Добавляем данные для каждого файла в HTML
        self.report_content += f"<tr><td>{file_path}</td><td>{summary.replace('\n', '<br>')}</td></tr>"

    def finish_report(self):
        # Заканчиваем HTML отчет
        self.report_content += """
        </table>
        </body>
        </html>
        """

    def save_report(self):
        # Сохраняем HTML отчет в файл
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(self.report_content)
        logging.info(f"HTML report saved to {self.output_file}")
