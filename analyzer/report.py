import logging
import os
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

class HTMLReport:
    """
    Generates an HTML report of code analysis results.
    """

    def __init__(self, output_file: str, template_file: str = 'report-template.html', project_name: str = 'Unnamed Project'):
        """
        Initializes the HTMLReport instance.

        :param output_file: The path to the output HTML file.
        :param template_file: The path to the HTML template file.
        :param project_name: The name of the project being analyzed.
        """
        self.output_file = output_file
        self.project_name = project_name
        self.scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report_data: List[Dict[str, Any]] = []
        self.env = Environment(
            loader=FileSystemLoader(searchpath=os.path.dirname(template_file) or '.'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        try:
            self.template = self.env.get_template(os.path.basename(template_file))
            logging.debug(f"Loaded template '{template_file}' successfully.")
        except Exception as e:
            logging.error(f"Failed to load template '{template_file}': {e}")
            raise

    def add_file_summary(self, file_path: str, issues: List[Dict[str, Any]]) -> None:
        """
        Adds the analysis results for a file to the report data.

        :param file_path: The path to the analyzed file.
        :param issues: A list of issues detected in the file.
        """
        logging.debug(f"Adding summary for file: {file_path}")
        self.report_data.append({
            'file_path': file_path,
            'issues': issues
        })

    def generate_report(self) -> None:
        """
        Generates the HTML report and writes it to the output file.
        """
        try:
            logging.info("Generating HTML report...")
            output_from_parsed_template = self.template.render(
                project_name=self.project_name,
                scan_time=self.scan_time,
                files=self.report_data
            )
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(output_from_parsed_template)
            logging.info(f"HTML report saved to {self.output_file}")
        except Exception as e:
            logging.error(f"Failed to generate HTML report: {e}")
            raise
