from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QComboBox, QCheckBox,
                             QProgressBar, QTextEdit)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool
import requests

class SearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a webtoon...")
        self.search_button = QPushButton("Search")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Or enter a direct manga URL...")
        self.lang_input = QLineEdit()
        self.lang_input.setPlaceholderText("Lang (e.g., en)")
        self.lang_input.setFixedWidth(80)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.lang_input)

        self.layout.addLayout(search_layout)
        self.layout.addLayout(url_layout)

class ImageFetcherSignals(QObject):
    finished = pyqtSignal(QPixmap)
    error = pyqtSignal(str)

class ImageFetcher(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = ImageFetcherSignals()

    @pyqtSlot()
    def run(self):
        try:
            headers = {
                'Referer': 'https://www.webtoons.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(self.url, stream=True, headers=headers)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.signals.finished.emit(pixmap)
        except requests.exceptions.RequestException as e:
            self.signals.error.emit(str(e))

class ResultsDisplay(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setSpacing(10)
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(10) # Limit concurrent image downloads

    def add_manga_item(self, title, cover_url):
        item = QListWidgetItem()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        cover_label = QLabel("Loading...")
        cover_label.setFixedSize(150, 200) # Give it a fixed size
        
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        
        layout.addWidget(cover_label)
        layout.addWidget(title_label)
        
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

        # Asynchronously fetch the image
        fetcher = ImageFetcher(cover_url)
        fetcher.signals.finished.connect(lambda pixmap: self.on_image_loaded(cover_label, pixmap))
        fetcher.signals.error.connect(lambda error: self.on_image_error(cover_label, error))
        self.threadpool.start(fetcher)

    def on_image_loaded(self, label, pixmap):
        label.setPixmap(pixmap.scaledToWidth(150))

    def on_image_error(self, label, error_msg):
        print(f"Failed to load cover image: {error_msg}")
        pixmap = QPixmap('gui/placeholder.png') # Fallback placeholder
        if not pixmap.isNull():
            label.setPixmap(pixmap.scaledToWidth(150))
        else:
            label.setText("Error")

class ChapterSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.all_button = QPushButton("All")
        self.all_button.setCheckable(True)
        self.single_input = QLineEdit()
        self.single_input.setPlaceholderText("e.g., 5")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g., 1-10")
        
        self.layout.addWidget(QLabel("Chapters:"))
        self.layout.addWidget(self.all_button)
        self.layout.addWidget(QLabel("Single:"))
        self.layout.addWidget(self.single_input)
        self.layout.addWidget(QLabel("Range:"))
        self.layout.addWidget(self.range_input)

class OptionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.format_selector = QComboBox()
        self.format_selector.addItems(["PDF", "CBZ", "None"])
        
        self.cleanup_checkbox = QCheckBox("Delete images after conversion")
        self.original_quality_checkbox = QCheckBox("Original-quality images (larger files)")
        
        self.layout.addWidget(QLabel("Format:"))
        self.layout.addWidget(self.format_selector)
        self.layout.addWidget(self.cleanup_checkbox)
        self.layout.addWidget(self.original_quality_checkbox)

class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.progress_bar = QProgressBar()
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.log_display)
