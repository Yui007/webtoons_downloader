# Webtoons Manga Downloader - GUI Usage

This document provides instructions on how to use the graphical user interface (GUI) for the Webtoons Manga Downloader.

## Main Window

The GUI provides a user-friendly interface to search for, select, and download your favorite webtoons.

![GUI Screenshot](gui/screenshot.PNG)

## How to Use

### 1. Searching for a Manga

-   **Search Bar**: Enter the name of the manga you want to find in the top search bar.
-   **Language (Optional)**: If you are searching for a manga in a language other than English, enter the two-letter language code (e.g., `id`, `es`, `fr`) in the "Lang" field next to the URL bar.
-   **Click Search**: Press the "Search" button to begin. The results will appear in the panel below.

### 2. Downloading via Direct URL

-   **URL Input**: If you already have the URL for the manga's main page, you can paste it directly into the URL input field.
-   **Language (Optional)**: Ensure the correct language code is set if the webtoon is not in English.
-   The downloader will automatically fetch the manga's title and episode list.

### 3. Selecting a Manga and Chapters

-   **Select from Results**: Click on a manga cover from the search results to select it.
-   **Choose Chapters**:
    -   **All**: Click the "All" button to download every chapter.
    -   **Single**: Enter a specific chapter number in the "Single" field.
    -   **Range**: Enter a range of chapters in the "Range" field (e.g., `1-10`).

### 4. Download Options

-   **Format**: Choose the output format for your download:
    -   **PDF**: Converts each chapter into a separate PDF file.
    -   **CBZ**: Converts each chapter into a separate CBZ archive, which is ideal for comic book readers.
    -   **None**: Downloads the chapter images as-is, without any conversion.
-   **Cleanup**: Check the "Delete images after conversion" box to automatically remove the raw image folders once the PDF or CBZ file has been created. This option is ignored if the format is "None".
-   **Original Quality**: Check "Original-quality images (larger files)" to download Webtoon's original source images instead of its bandwidth-optimized versions. This increases download size and applies to every output format. PDF conversion may still re-encode the images.

### 5. Start Downloading

-   **Download Button**: Once you have configured your selection and options, click the "Download" button.
-   **Progress**: You can monitor the download progress in the status panel at the bottom. The progress bar will update as chapters are downloaded and converted, and the log window will show detailed messages for each step. The downloader now supports parallel downloads, so you will see multiple chapters being processed at once.
