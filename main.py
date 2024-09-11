import logging
import argparse
from analyzer import CodeAnalyzer
from report import HTMLReport
from config import GROQ_API_KEY

def main():
    parser = argparse.ArgumentParser(description="Analyze source code files for vulnerabilities.")
    parser.add_argument('directory', type=str, help="Directory to analyze")
    parser.add_argument('--output', type=str, default='report.html', help="Output HTML file for the report")
    parser.add_argument('--max-retries', type=int, default=5, help="Max retries for API requests")
    parser.add_argument('--timeout', type=float, default=20.0, help="Timeout for API requests")
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level")
    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)
    html_report = HTMLReport(output_file=args.output)
    html_report.start_report()
    analyzer = CodeAnalyzer(directory=args.directory, max_retries=args.max_retries, timeout=args.timeout)
    analyzer.analyze(html_report)
    html_report.finish_report()


if __name__ == "__main__":
    main()
