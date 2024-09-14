# tests/test_html_report.py

import unittest
import os
from analyzer.report import HTMLReport

class TestHTMLReport(unittest.TestCase):
    def setUp(self):
        self.output_file = 'test_report.html'
        self.report = HTMLReport(self.output_file, 'report-template.html')

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_add_file_summary_and_generate_report(self):
        issues = [
            {'severity': 'HIGH', 'description': 'Test issue 1', 'line': 10},
            {'severity': 'LOW', 'description': 'Test issue 2', 'line': 20},
        ]
        self.report.add_file_summary('test_file.py', issues)
        self.report.generate_report()

        # Check if output file is created
        self.assertTrue(os.path.exists(self.output_file))

        # Optionally, check the contents of the file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('test_file.py', content)
            self.assertIn('Test issue 1', content)
            self.assertIn('HIGH', content)
            self.assertIn('10', content)

if __name__ == '__main__':
    unittest.main()
