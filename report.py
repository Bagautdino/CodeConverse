import logging
import markdown2

class HTMLReport:
    def __init__(self, output_file):
        self.output_file = output_file
        self.report_content = ""
        self.template = ""
        with open('report-template.html', 'r', encoding='utf-8') as f:
            self.template = f.read()

    def start_report(self):
        self.report_content = ""

    def add_file_summary(self, file_path, summary):
        self.report_content += markdown2.markdown(self.template.format(file_path=file_path, summary=summary))
        self.report_content += f"<tr><td>{file_path}</td><td>{summary.replace('\n', '<br>')}</td></tr>"

    def finish_report(self):
        final_report = self.template.replace('{{ rows }}', self.report_content)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(final_report)
        logging.info(f"HTML report saved to {self.output_file}")
