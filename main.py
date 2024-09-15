import logging
import argparse
import os
from analyzer.analyzer import CodeAnalyzer
from analyzer.report import HTMLReport

def main():
    parser = argparse.ArgumentParser(description="Analyze source code files for vulnerabilities.")
    parser.add_argument('directory', type=str, nargs='?', default='.', help="Directory to analyze")
    parser.add_argument('--output', type=str, default='report.html', help="Output HTML file for the report")
    parser.add_argument('--max-retries', type=int, default=5, help="Max retries for API requests")
    parser.add_argument('--timeout', type=float, default=20.0, help="Timeout for API requests")
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=args.log_level.upper(),
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("code_analyzer.log"),
            logging.StreamHandler()
        ]
    )

    # Validate the directory
    if not os.path.isdir(args.directory):
        logging.error(f"The directory '{args.directory}' does not exist or is not a directory.")
        exit(1)

    # Extract the project name from the directory path
    project_name = os.path.basename(os.path.abspath(args.directory)) or 'Unnamed Project'

    # Log the project name for confirmation
    logging.info(f"Project Name: {project_name}")

    try:
        # Create instances of CodeAnalyzer and HTMLReport
        html_report = HTMLReport(output_file=args.output, project_name=project_name)
        analyzer = CodeAnalyzer(directory=args.directory, max_retries=args.max_retries, timeout=args.timeout)

        # Run the analysis and generate the report
        analyzer.analyze(html_report)
        html_report.generate_report()
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
