# cli/argument_parser.py

import argparse

def setup_parser():
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Webtoons Manga Downloader")

    # Mode selection
    parser.add_argument("--gui", action="store_true", help="Run the graphical user interface.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode.")
    
    # Search functionality
    parser.add_argument("--search", type=str, help="Search for a manga by keyword.")
    parser.add_argument("--lang", type=str, default="en", help="Language of the webtoon (e.g., en, id). Default is 'en'.")
    
    # URL functionality
    parser.add_argument("--url", type=str, help="Scrape and list episodes for a given manga URL.")
    
    # Download functionality
    parser.add_argument("--download", action="store_true", help="Enable download mode.")
    parser.add_argument("--range", type=str, help="Download a range of episodes (e.g., 1-10).")
    parser.add_argument("--single", type=int, help="Download a single episode.")
    parser.add_argument("--all", action="store_true", help="Download all episodes.")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use for downloading (default: 10).")
    parser.add_argument(
        "--original-quality",
        action="store_true",
        help="Download original-quality source images (uses more bandwidth and storage).",
    )
    
    # Format conversion
    parser.add_argument("--format", type=str, choices=["pdf", "cbz"], help="Convert downloaded chapters to PDF or CBZ.")
    
    # Cleanup
    parser.add_argument("--clean", action="store_true", help="Remove raw images after conversion.")
    
    return parser
