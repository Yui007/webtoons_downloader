# main.py

from cli.argument_parser import setup_parser
from cli.interactive_menu import app as interactive_app
from gui.main import run_gui
from core.scraper import search_manga, scrape_episodes, scrape_chapter_images
from core.downloader import download_chapter
from core.converter import convert_to_pdf, convert_to_cbz
from core.cleaner import clean_chapter_images
from utils.logger import logger
from utils.helpers import parse_views
import re
import os
import sys
import concurrent.futures
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

def process_chapter(chapter_data):
    """Worker function to process a single chapter."""
    episode, manga_title, args = chapter_data
    try:
        logger.info(f"Processing Episode {episode['number']}: {episode['title']}")
        image_urls = scrape_chapter_images(
            episode['url'],
            original_quality=args.original_quality,
        )
        if image_urls:
            chapter_dir = download_chapter(manga_title, episode['number'], image_urls, args.threads)
            if args.format and chapter_dir:
                output_filename = f"{manga_title} - Episode {episode['number']}.{args.format}"
                output_path = os.path.join(os.path.dirname(chapter_dir), output_filename)
                if args.format == 'pdf':
                    convert_to_pdf(chapter_dir, output_path)
                elif args.format == 'cbz':
                    convert_to_cbz(chapter_dir, output_path)
                
                if args.clean:
                    clean_chapter_images(chapter_dir)
        return f"Successfully processed Episode {episode['number']}"
    except Exception as e:
        logger.error(f"Failed to process Episode {episode['number']}: {e}")
        return f"Failed to process Episode {episode['number']}"

def main():
    """Main function to run the application."""
    if '-i' in sys.argv or '--interactive' in sys.argv:
        # Remove the interactive flag to prevent argparse from seeing it
        if '-i' in sys.argv:
            sys.argv.remove('-i')
        if '--interactive' in sys.argv:
            sys.argv.remove('--interactive')
        interactive_app()
        return
    
    if '--gui' in sys.argv:
        run_gui()
        return

    parser = setup_parser()
    args = parser.parse_args()
    console = Console()

    if args.search:
        logger.info(f"Searching for: {args.search}")
        results = search_manga(args.search, args.lang)
        if results:
            table = Table(
                show_header=True,
                header_style="bold magenta on white",
                border_style="bright_blue",
                title="Search Results",
                title_style="bold yellow",
                row_styles=["on #333333", "on #222222"]
            )
            table.add_column("#", style="dim", width=3)
            table.add_column("Title", style="bold white", no_wrap=True)
            table.add_column("Author", style="cyan")
            table.add_column("Views", justify="right", style="light_green")
            table.add_column("URL", style="blue", no_wrap=True)

            for i, result in enumerate(results, 1):
                row_style = ""
                try:
                    if parse_views(result['views']) > 100_000_000:
                        row_style = "bold gold1"
                except (ValueError, TypeError):
                    pass

                table.add_row(
                    str(i),
                    result['title'],
                    result['author'],
                    result['views'],
                    result['url'],
                    style=row_style
                )
            console.print(table)
    
    elif args.url and args.download:
        logger.info(f"Starting download process for: {args.url}")
        # Detect language from URL to override default from args
        lang_from_url_match = re.search(r'webtoons.com/([a-z]{2,3})/', args.url)
        lang = lang_from_url_match.group(1) if lang_from_url_match else args.lang

        episodes = scrape_episodes(args.url, lang)
        
        if not episodes:
            logger.warning("No episodes found to download.")
            return

        # Extract manga title from URL for directory naming
        manga_title_match = re.search(rf'/{lang}/([^/]+)/([^/]+)/', args.url)
        manga_title = manga_title_match.group(2).replace('-', ' ').title() if manga_title_match else "Unknown Manga"

        episodes_to_download = []
        if args.all:
            episodes_to_download = episodes
        elif args.single:
            episodes_to_download = [e for e in episodes if e['number'] == args.single]
        elif args.range:
            start, end = map(int, args.range.split('-'))
            episodes_to_download = [e for e in episodes if start <= e['number'] <= end]

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            chapter_data_list = [(episode, manga_title, args) for episode in episodes_to_download]
            
            results = list(tqdm(executor.map(process_chapter, chapter_data_list), total=len(episodes_to_download), desc="Processing Chapters"))

            for result in results:
                logger.info(result)

    elif args.url:
        logger.info(f"Scraping episodes for: {args.url}")
        # Detect language from URL to override default from args
        lang_from_url_match = re.search(r'webtoons.com/([a-z]{2,3})/', args.url)
        lang = lang_from_url_match.group(1) if lang_from_url_match else args.lang
        
        episodes = scrape_episodes(args.url, lang)
        if episodes:
            for episode in episodes:
                print(f"Episode {episode['number']}: {episode['title']}")
    
    else:
        # If no other args, and not interactive, show help.
        if len(sys.argv) == 1:
            parser.print_help()

if __name__ == "__main__":
    main()
