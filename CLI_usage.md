# Webtoons Manga Downloader - CLI Usage

This document provides instructions on how to use both the argument-based and interactive command-line interfaces (CLIs) for the Webtoons Manga Downloader.

## Argument-Based CLI

The argument-based CLI allows you to perform all actions in a single command. This is ideal for scripting and automation.

### Searching for a Manga

To search for a manga, use the `--search` flag followed by your search query.

```bash
python main.py --search "Love"
```

### Downloading a Manga

To download a manga, you need to provide the manga's URL with the `--url` flag and enable download mode with `--download`.

**Download a range of episodes:**

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --range 1-10
```

**Download a single episode:**

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --single 5
```

**Download all episodes:**

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --all
```

### Original-Quality Images

Webtoon normally provides bandwidth-optimized images. Add `--original-quality` to download the original source images instead. This option uses more bandwidth and storage and applies to raw image folders, CBZ, and PDF output. PDF conversion may still re-encode the images.

```bash
python main.py --url "https://www.webtoons.com/en/action/overwatch/list?title_no=9843" --download --single 1 --format cbz --original-quality
```

### Language Selection

You can specify the language of the webtoon you want to download or Search using the `--lang` flag. This is useful for Searching and downloading from non-English versions of Webtoons.

```bash
# Search for a manga in Indonesian
python main.py --search "love" --lang id

### Format Conversion

You can convert the downloaded chapters to PDF or CBZ format using the `--format` flag.

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --range 1-5 --format pdf
```

### Cleanup

To automatically delete the raw image folders after conversion, use the `--clean` flag.

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --all --format cbz --clean
```

### Parallel Downloading

To speed up the download process, you can use multiple threads for downloading images. Use the `--threads` flag to specify the number of threads (default is 10).

```bash
python main.py --url "https://www.webtoons.com/en/fantasy/the-lone-necromancer/list?title_no=3690" --download --all --threads 20
```

## Interactive CLI

The interactive CLI provides a user-friendly, step-by-step guide for downloading your favorite webtoons. To start the interactive mode, use the `-i` or `--interactive` flag.

```bash
python main.py --interactive
```

The interactive menu will guide you through the following steps:

1.  **Choose Input Method:** You can either search for a webtoon by name or provide a direct URL.
2.  **Language Selection:** If you choose to search, you will be prompted to enter a language code (e.g., `en` for English, `id` for Indonesian).
3.  **Select a Manga:** If you searched, you'll be presented with a list of results to choose from.
4.  **Choose Chapters:** Select whether you want to download all episodes, a specific range, or a single episode.
5.  **Select Format:** Choose between PDF and CBZ for the output format.
6.  **Cleanup:** Decide if you want to delete the raw image folders after the conversion is complete.
7.  **Choose Image Quality:** Decide whether to download the larger original-quality source images.
8.  **Set Thread Count:** Specify the number of threads to use for downloading to accelerate the process.

The interactive mode is designed to be intuitive and requires no prior knowledge of the command-line arguments.
