import typer
from rich.console import Console
from rich.panel import Panel
import os
import re
import concurrent.futures
from tqdm import tqdm
from core.scraper import search_manga, scrape_episodes, scrape_chapter_images
from core.downloader import download_chapter
from core.converter import convert_to_pdf, convert_to_cbz
from core.cleaner import clean_chapter_images
from utils.config import OUTPUT_DIR
from utils.helpers import create_directory

app = typer.Typer()
console = Console()

def get_initial_choice():
    """Prompt the user to choose between searching or providing a URL."""
    console.print("\n[bold green]Choose an option:[/bold green]")
    console.print("1. Search for a webtoon")
    console.print("2. Provide a URL directly")

    while True:
        choice = typer.prompt("Choose an option (1-2)")
        if choice in ["1", "2"]:
            return choice
        else:
            console.print("Invalid choice. Please select 1 or 2.", style="bold red")

def get_search_query():
    """Prompt the user for a search query."""
    return typer.prompt("\nEnter the name of the webtoon you want to search for")

def get_manga_url():
    """Prompt the user for a manga URL."""
    return typer.prompt("\nEnter the URL of the webtoon")

def get_language_choice():
    """Prompt the user for the language."""
    return typer.prompt("\nEnter the language (e.g., en, id)", default="en")

def get_format_choice():
    """Prompt the user to choose the output format."""
    console.print("\n[bold green]Output Format:[/bold green]")
    console.print("1. PDF")
    console.print("2. CBZ")

    while True:
        choice = typer.prompt("Choose an option (1-2)")
        if choice == "1":
            return "pdf"
        elif choice == "2":
            return "cbz"
        else:
            console.print("Invalid choice. Please select 1 or 2.", style="bold red")

def get_cleanup_choice():
    """Prompt the user whether to clean up image files."""
    return typer.confirm("\nDo you want to delete the raw image folders after conversion?")


def get_original_quality_choice():
    """Prompt the user whether to download original-quality source images."""
    return typer.confirm(
        "\nDownload original-quality images? (larger files)",
        default=False,
    )


def get_chapter_choice(episodes):
    """Prompt the user to choose which chapters to download."""
    console.print("\n[bold green]Download Options:[/bold green]")
    console.print("1. All episodes")
    console.print("2. A range of episodes (e.g., 1-10)")
    console.print("3. A single episode")

    while True:
        choice = typer.prompt("Choose an option (1-3)")
        if choice in ["1", "2", "3"]:
            return choice
        else:
            console.print("Invalid choice. Please select 1, 2, or 3.", style="bold red")

def get_chapter_range(max_episode):
    """Prompt the user for a chapter range."""
    while True:
        try:
            chapter_range = typer.prompt(f"Enter chapter range (e.g., 1-10), max is {max_episode}")
            start, end = map(int, chapter_range.split('-'))
            if 1 <= start <= end <= max_episode:
                return start, end
            else:
                console.print(f"Invalid range. Please enter a valid range within 1-{max_episode}.", style="bold red")
        except ValueError:
            console.print("Invalid format. Please use the format 'start-end'.", style="bold red")

def get_single_chapter(max_episode):
    """Prompt the user for a single chapter."""
    while True:
        try:
            chapter_num = int(typer.prompt(f"Enter chapter number (1-{max_episode})"))
            if 1 <= chapter_num <= max_episode:
                return chapter_num
            else:
                console.print(f"Invalid chapter number. Please enter a number between 1 and {max_episode}.", style="bold red")
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="bold red")

def get_num_threads():
    """Prompt the user for the number of threads."""
    while True:
        try:
            num_threads = int(typer.prompt("Enter the number of threads for downloading (default: 10)", default=10))
            if num_threads > 0:
                return num_threads
            else:
                console.print("Please enter a positive number.", style="bold red")
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="bold red")

def select_manga_from_results(results):
    """Display search results and prompt the user to select a manga."""
    if not results:
        console.print("No results found.", style="bold red")
        return None

    console.print("\n[bold green]Search Results:[/bold green]")
    for i, result in enumerate(results):
        console.print(f"{i + 1}. {result['title']} by {result['author']} ({result['views']})")

    while True:
        try:
            choice = typer.prompt(f"Select a manga (1-{len(results)})")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(results):
                return results[choice_index]
            else:
                console.print("Invalid selection. Please try again.", style="bold red")
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="bold red")

def process_chapter_interactive(chapter_data):
    """Worker function for interactive chapter processing."""
    chapter, manga_title, output_format, cleanup, num_threads, original_quality = chapter_data
    try:
        console.print(f"\nProcessing: [bold cyan]{chapter['title']}[/bold cyan]")
        
        image_urls = scrape_chapter_images(
            chapter['url'],
            original_quality=original_quality,
        )
        if not image_urls:
            console.print(f"Could not find images for {chapter['title']}.", style="bold red")
            return
        chapter_dir = download_chapter(manga_title, chapter['number'], image_urls, num_threads)
        
        if output_format == 'pdf':
            output_path = os.path.join(OUTPUT_DIR, manga_title, f"{manga_title}_E{chapter['number']}.pdf")
            convert_to_pdf(chapter_dir, output_path)
        elif output_format == 'cbz':
            output_path = os.path.join(OUTPUT_DIR, manga_title, f"{manga_title}_E{chapter['number']}.cbz")
            convert_to_cbz(chapter_dir, output_path)
        if cleanup:
            clean_chapter_images(chapter_dir)
    except Exception as e:
        console.print(f"An error occurred while processing {chapter['title']}: {e}", style="bold red")

@app.command()
def main():
    """
    Run the interactive webtoon downloader.
    """
    console.print(Panel("Welcome to the Interactive Webtoon Downloader!", title="Welcome", style="bold green"))

    initial_choice = get_initial_choice()
    selected_manga = None

    if initial_choice == "1":
        lang = get_language_choice()
        query = get_search_query()
        search_results = search_manga(query, lang)
        selected_manga = select_manga_from_results(search_results)
    elif initial_choice == "2":
        url = get_manga_url()
        lang_match = re.search(r'webtoons.com/([a-z]{2,3})/', url)
        lang = lang_match.group(1) if lang_match else 'en'
        # We need to get the title from the URL for display purposes
        # This is a simplified way to get a title. A more robust solution
        # might involve scraping the page for the actual title.
        title_match = re.search(rf'/{lang}/([^/]+)/([^/]+)/', url)
        title = title_match.group(2).replace('-', ' ').title() if title_match else "Unknown Manga"
        selected_manga = {'url': url, 'title': title}


    if selected_manga:
        console.print(f"\nYou selected: [bold cyan]{selected_manga['title']}[/bold cyan]")
        
        episodes = scrape_episodes(selected_manga['url'], lang)
        if not episodes:
            console.print("Could not retrieve episode list.", style="bold red")
            return

        console.print(f"Found {len(episodes)} episodes.")

        chapter_choice = get_chapter_choice(episodes)
        
        chapters_to_download = []
        if chapter_choice == "1":
            chapters_to_download = episodes
        elif chapter_choice == "2":
            start, end = get_chapter_range(len(episodes))
            chapters_to_download = episodes[start-1:end]
        elif chapter_choice == "3":
            chapter_num = get_single_chapter(len(episodes))
            chapters_to_download = [episodes[chapter_num-1]]

        if chapters_to_download:
            output_format = get_format_choice()
            cleanup = get_cleanup_choice()
            original_quality = get_original_quality_choice()
            num_threads = get_num_threads()

            console.print(f"\n[bold green]Starting download...[/bold green]")
            
            manga_title = selected_manga['title'].replace(' ', '_')
            create_directory(os.path.join(OUTPUT_DIR, manga_title))

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                chapter_data_list = [
                    (chapter, manga_title, output_format, cleanup, num_threads, original_quality)
                    for chapter in chapters_to_download
                ]
                
                results = list(tqdm(executor.map(process_chapter_interactive, chapter_data_list), total=len(chapters_to_download), desc="Processing Chapters"))

            console.print("\n[bold green]All tasks completed![/bold green]")

if __name__ == "__main__":
    app()
