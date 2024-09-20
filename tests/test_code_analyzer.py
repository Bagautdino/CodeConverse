# tests/test_code_analyzer.py
# DEPRECATED since 1.1.2

import unittest
from unittest.mock import patch, MagicMock
from analyzer.analyzer import CodeAnalyzer
from analyzer.report import HTMLReport


class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer(directory='test_directory')
        self.html_report = MagicMock()

    @patch('code_analyzer.Groq')
    def test_process_code(self, mock_groq):
        # Mock the Groq client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"issues": [{"severity": "HIGH", "description": "Test issue", "line": 1}]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client

        # Test data
        file_path = 'test_file.py'
        model_token = 'test_model_token'
        content = 'print("Hello, World!")'

        result = self.analyzer.process_code(file_path, model_token, content)

        # Assertions
        self.assertIsInstance(result, str)
        self.assertIn('"severity": "HIGH"', result)
        mock_client.chat.completions.create.assert_called_once()

    @patch('code_analyzer.os.walk')
    @patch('code_analyzer.CodeAnalyzer.read_file')
    @patch.object(CodeAnalyzer, 'process_code')
    def test_analyze(self, mock_process_code, mock_read_file, mock_os_walk):
        # Setup the mock
        mock_os_walk.return_value = [
            ('test_directory', [], ['test_file.py'])
        ]
        mock_read_file.return_value = 'print("Hello, World!")'
        mock_process_code.return_value = '{"issues": []}'

        # Call the analyze method
        self.analyzer.analyze(self.html_report)

        # Assertions
        mock_read_file.assert_called_with('test_directory/test_file.py')
        mock_process_code.assert_called_once()
        self.html_report.add_file_summary.assert_called_once_with('test_directory/test_file.py', '{"issues": []}')

    def test_split_content(self):
        content = 'A' * 12000  # Content longer than 5000 characters
        chunks = self.analyzer.split_content(content)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 5000)
        self.assertEqual(len(chunks[1]), 5000)
        self.assertEqual(len(chunks[2]), 2000)

if __name__ == '__main__':
    unittest.main()
