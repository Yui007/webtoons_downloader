import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

import main as argument_cli
from cli.argument_parser import setup_parser
from cli.interactive_menu import (
    get_original_quality_choice,
    process_chapter_interactive,
)
from core.scraper import get_original_image_url, scrape_chapter_images
from gui.main import DownloadWorker
from gui.widgets import OptionsPanel


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        return None


class OriginalImageUrlTests(unittest.TestCase):
    def test_url_without_q90_is_unchanged(self):
        image_url = "https://example.com/page.jpg?token=a%20b#panel"

        self.assertEqual(get_original_image_url(image_url), image_url)

    def test_only_q90_parameter_is_removed(self):
        image_url = (
            "https://example.com/page.jpg?token=abc&type=q90&empty=&size=large#panel"
        )

        self.assertEqual(
            get_original_image_url(image_url),
            "https://example.com/page.jpg?token=abc&empty=&size=large#panel",
        )

    def test_other_type_values_are_preserved(self):
        image_url = "https://example.com/page.jpg?type=q80"

        self.assertEqual(get_original_image_url(image_url), image_url)

    def test_scraper_preserves_default_urls_and_order(self):
        urls = [
            "https://example.com/001.jpg?type=q90",
            "https://example.com/002.jpg?token=abc&type=q90",
        ]
        html = (
            '<div id="_imageList">'
            + "".join(
                f'<img class="_images" data-url="{url}">' for url in urls
            )
            + "</div>"
        ).encode()

        with patch(
            "core.scraper.requests.get",
            return_value=FakeResponse(html),
        ):
            default_urls = scrape_chapter_images("https://example.com/episode")
            original_urls = scrape_chapter_images(
                "https://example.com/episode",
                original_quality=True,
            )

        self.assertEqual(default_urls, urls)
        self.assertEqual(
            original_urls,
            [
                "https://example.com/001.jpg",
                "https://example.com/002.jpg?token=abc",
            ],
        )


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_argument_parser_defaults_original_quality_off(self):
        args = setup_parser().parse_args([])

        self.assertFalse(args.original_quality)

    def test_argument_parser_accepts_original_quality(self):
        args = setup_parser().parse_args(["--original-quality"])

        self.assertTrue(args.original_quality)

    @patch("main.download_chapter", return_value="chapter")
    @patch("main.scrape_chapter_images", return_value=["image"])
    def test_argument_worker_forwards_original_quality(
        self,
        scrape_images,
        _download_chapter,
    ):
        args = SimpleNamespace(
            threads=1,
            format=None,
            clean=False,
            original_quality=True,
        )

        result = argument_cli.process_chapter(
            ({"number": 1, "title": "Episode", "url": "episode-url"}, "Title", args)
        )

        self.assertEqual(result, "Successfully processed Episode 1")
        scrape_images.assert_called_once_with(
            "episode-url",
            original_quality=True,
        )

    @patch("cli.interactive_menu.download_chapter", return_value="chapter")
    @patch("cli.interactive_menu.scrape_chapter_images", return_value=["image"])
    def test_interactive_worker_forwards_original_quality(
        self,
        scrape_images,
        _download_chapter,
    ):
        process_chapter_interactive(
            (
                {"number": 1, "title": "Episode", "url": "episode-url"},
                "Title",
                None,
                False,
                1,
                True,
            )
        )

        scrape_images.assert_called_once_with(
            "episode-url",
            original_quality=True,
        )

    @patch("cli.interactive_menu.typer.confirm", return_value=False)
    def test_interactive_prompt_defaults_original_quality_off(self, confirm):
        self.assertFalse(get_original_quality_choice())
        confirm.assert_called_once_with(
            "\nDownload original-quality images? (larger files)",
            default=False,
        )

    @patch("gui.main.download_chapter", return_value=None)
    @patch("gui.main.scrape_chapter_images", return_value=["image"])
    def test_gui_worker_forwards_original_quality(
        self,
        scrape_images,
        _download_chapter,
    ):
        worker = DownloadWorker(
            "Title",
            {"number": 1, "url": "episode-url"},
            "None",
            False,
            original_quality=True,
        )

        worker.run()

        scrape_images.assert_called_once_with(
            "episode-url",
            original_quality=True,
        )

    def test_gui_checkbox_is_present_and_unchecked(self):
        panel = OptionsPanel()

        self.assertEqual(
            panel.original_quality_checkbox.text(),
            "Original-quality images (larger files)",
        )
        self.assertFalse(panel.original_quality_checkbox.isChecked())


if __name__ == "__main__":
    unittest.main()
