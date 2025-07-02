import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QPlainTextEdit, QProgressBar,
    QCheckBox, QListWidget, QListWidgetItem, QLabel, QGroupBox,
    QAbstractItemView
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal

# --- CONFIGURATION ---
# --------------------------------------------
# These are the default settings. They can be changed by the user in the GUI.

# Default for the "Use Date Subfolders" checkbox
DEFAULT_USE_DATE_SUBFOLDERS = True

# Default selected items for the date organization list
DEFAULT_DATE_ORGANIZATION_CATEGORIES = {"Media", "Documents", "Archives"}

# The main file type mapping dictionary
FILE_TYPE_MAPPINGS = {
    # === Media ===
    # Images
    ".png": ("Media", "Images"), ".jpg": ("Media", "Images"), ".jpeg": ("Media", "Images"),
    ".gif": ("Media", "Images"), ".svg": ("Media", "Images"), ".webp": ("Media", "Images"),
    ".bmp": ("Media", "Images"), ".tiff": ("Media", "Images"), ".tif": ("Media", "Images"),
    ".heic": ("Media", "Images", "HEIC"), ".heif": ("Media", "Images", "HEIC"),
    ".ico": ("Media", "Images", "Icons"),
    # Camera RAW Images
    ".raw": ("Media", "Images", "RAW"), ".cr2": ("Media", "Images", "RAW"),  # Canon
    ".nef": ("Media", "Images", "RAW"),  # Nikon
    ".arw": ("Media", "Images", "RAW"),  # Sony
    ".dng": ("Media", "Images", "RAW"),  # Adobe Digital Negative
    # Video
    ".mp4": ("Media", "Video"), ".mov": ("Media", "Video"), ".avi": ("Media", "Video"),
    ".mkv": ("Media", "Video"), ".wmv": ("Media", "Video"), ".flv": ("Media", "Video"),
    ".webm": ("Media", "Video"), ".mpg": ("Media", "Video"), ".mpeg": ("Media", "Video"),
    # Audio
    ".mp3": ("Media", "Audio"), ".wav": ("Media", "Audio"), ".flac": ("Media", "Audio"),
    ".m4a": ("Media", "Audio"), ".aac": ("Media", "Audio"), ".ogg": ("Media", "Audio"),
    ".wma": ("Media", "Audio"),
    # Subtitles
    ".srt": ("Media", "Subtitles"), ".sub": ("Media", "Subtitles"),
    ".ass": ("Media", "Subtitles"), ".ssa": ("Media", "Subtitles"),
    ".vtt": ("Media", "Subtitles"), ".idx": ("Media", "Subtitles"),

    # === Documents & Text ===
    ".pdf": ("Documents", "PDFs"),
    ".doc": ("Documents", "Word"), ".docx": ("Documents", "Word"),
    ".odt": ("Documents", "OpenDocument Text"),
    ".txt": ("Documents", "Text"), ".rtf": ("Documents", "Text"), ".md": ("Documents", "Markdown"),
    ".epub": ("Documents", "Ebooks"), ".mobi": ("Documents", "Ebooks"),

    # === Data & Spreadsheets ===
    ".xls": ("Data", "Spreadsheets"), ".xlsx": ("Data", "Spreadsheets"),
    ".ods": ("Data", "OpenDocument Spreadsheets"),
    ".csv": ("Data", "CSV"), ".tsv": ("Data", "TSV"),
    ".json": ("Data", "JSON"), ".xml": ("Data", "XML"),
    ".sqlite": ("Data", "Databases"), ".db": ("Data", "Databases"),

    # === Productivity & Office ===
    ".ppt": ("Productivity", "Presentations"), ".pptx": ("Productivity", "Presentations"),
    ".odp": ("Productivity", "OpenDocument Presentations"),
    ".key": ("Productivity", "Keynote Presentations"),

    # === Archives ===
    ".zip": ("Archives",), ".rar": ("Archives",), ".tar": ("Archives",), ".gz": ("Archives",),
    ".bz2": ("Archives",), ".7z": ("Archives",), ".arj": ("Archives",),

    # === Projects & Design ===
    # 3D
    ".blend": ("Projects", "Blender"), ".blend1": ("Projects", "Blender", "Backups"),
    ".obj": ("Projects", "3D_Models"), ".fbx": ("Projects", "3D_Models"),
    ".stl": ("Projects", "3D_Models"), ".dae": ("Projects", "3D_Models"),
    ".3ds": ("Projects", "3D_Models"), ".mtl": ("Projects", "3D_Models"),
    # Adobe
    ".psd": ("Projects", "Adobe", "Photoshop"), ".ai": ("Projects", "Adobe", "Illustrator"),
    ".prproj": ("Projects", "Adobe", "PremierePro"), ".aep": ("Projects", "Adobe", "AfterEffects"),
    # Other Design
    ".fig": ("Projects", "Figma"), ".sketch": ("Projects", "Sketch"),
    ".pdn": ("Projects", "PaintNET"),
    # CAD
    ".dwg": ("Projects", "CAD"), ".dxf": ("Projects", "CAD"),
    # Digital Audio Workstations (DAW)
    ".flp": ("Projects", "DAW", "FL_Studio"), ".als": ("Projects", "DAW", "Ableton"),
    ".mid": ("Projects", "DAW", "MIDI"), ".midi": ("Projects", "DAW", "MIDI"),
    # Video Editing
    ".veg": ("Projects", "Vegas"),

    # === Code & Scripts ===
    ".py": ("Code", "Python"), ".ipynb": ("Code", "Python", "Jupyter"),
    ".js": ("Code", "JavaScript"), ".ts": ("Code", "TypeScript"),
    ".html": ("Code", "HTML"), ".htm": ("Code", "HTML"),
    ".css": ("Code", "CSS"), ".scss": ("Code", "Sass"),
    ".java": ("Code", "Java"), ".jar": ("Code", "Java", "JARs"),
    ".cs": ("Code", "CSharp"), ".cpp": ("Code", "C++"), ".c": ("Code", "C"),
    ".go": ("Code", "Go"), ".rb": ("Code", "Ruby"), ".swift": ("Code", "Swift"), ".php": ("Code", "PHP"),
    ".lua": ("Code", "Lua"),
    ".sh": ("Code", "Shell"), ".bat": ("Code", "Batch"),
    ".yml": ("Code", "Config"), ".yaml": ("Code", "Config"), ".ini": ("Code", "Config"), ".conf": ("Code", "Config"),
    # Shaders
    ".glsl": ("Code", "Shaders"), ".hlsl": ("Code", "Shaders"), ".cginc": ("Code", "Shaders"),
    ".shader": ("Code", "Shaders"), ".vert": ("Code", "Shaders"), ".frag": ("Code", "Shaders"),
    ".geom": ("Code", "Shaders"), ".comp": ("Code", "Shaders"), ".usf": ("Code", "Shaders"),
    ".spv": ("Code", "Shaders"), ".metal": ("Code", "Shaders"), ".fx": ("Code", "Shaders"),


    # === Gaming & Modding ===
    # Valve / Source Engine
    ".vpk": ("Gaming", "Valve", "Packages"), ".vps": ("Gaming", "Valve", "Particles"),
    ".gcf": ("Gaming", "Valve", "Packages"), ".gma": ("Gaming", "Valve", "GarrysModAddons"),
    ".bsp": ("Gaming", "Valve", "Maps"), ".vmf": ("Gaming", "Valve", "MapSources"),
    ".vmt": ("Gaming", "Valve", "Materials"), ".vtf": ("Gaming", "Valve", "Materials"),
    ".mdl": ("Gaming", "Valve", "Models"), ".smd": ("Gaming", "Valve", "ModelSources"),
    ".dem": ("Gaming", "Valve", "Demos"),
    # Roblox
    ".rbxl": ("Gaming", "Roblox", "Places"), ".rbxlx": ("Gaming", "Roblox", "Places"),
    ".rbxm": ("Gaming", "Roblox", "Models"), ".rbxmx": ("Gaming", "Roblox", "Models"),
    # Minecraft
    ".nbs": ("Gaming", "Minecraft", "NoteblockStudio"),

    # === System & Executables ===
    ".exe": ("System", "Executables"), ".msi": ("System", "Installers"),
    ".deb": ("System", "Installers", "Linux"), ".rpm": ("System", "Installers", "Linux"),
    ".dmg": ("System", "Installers", "macOS"), ".pkg": ("System", "Installers", "macOS"),
    ".iso": ("System", "DiskImages"), ".vhd": ("System", "VirtualDisks"), ".vmdk": ("System", "VirtualDisks"),
    ".ttf": ("System", "Fonts"), ".otf": ("System", "Fonts"), ".woff": ("System", "Fonts"), ".woff2": ("System", "Fonts"),
}

# Folder for files with unmapped extensions or no extension
DEFAULT_FOLDER_PATH = ("Other",)
# -----------------------------
# --- END OF CONFIGURATION ----


# Worker class for handling file operations in a separate thread
class SorterWorker(QObject):
    """
    Runs the file sorting process in a background thread to keep the GUI responsive.
    Emits signals to update the GUI with progress.
    """
    # Signals to communicate with the main GUI thread
    progress = pyqtSignal(str)              # For log messages
    progressBar = pyqtSignal(int)           # For progress bar updates (0-100)
    finished = pyqtSignal(int, int)         # (files_moved, files_skipped)

    def __init__(self, target_dir, use_date, date_categories):
        super().__init__()
        self.target_dir = target_dir
        self.use_date_subfolders = use_date
        self.date_organization_categories = date_categories
        self.is_running = True

    def run(self):
        """The main logic for sorting files, adapted for the GUI."""
        self.progress.emit(f"--- Starting file organization in: {self.target_dir} ---")
        
        # This script's name, to avoid moving itself if it's in the target dir
        script_filename = os.path.basename(__file__)
        
        files_to_process = [f for f in os.listdir(self.target_dir) if os.path.isfile(os.path.join(self.target_dir, f)) and f != script_filename]
        total_files = len(files_to_process)
        if total_files == 0:
            self.progress.emit("No user files found to sort in the directory.")
            self.finished.emit(0, 0)
            return

        files_moved_count = 0
        files_skipped_count = 0

        for i, filename in enumerate(files_to_process):
            if not self.is_running:
                break

            source_file_path = os.path.join(self.target_dir, filename)

            file_root, file_extension = os.path.splitext(filename)
            file_extension = file_extension.lower()

            path_parts = FILE_TYPE_MAPPINGS.get(file_extension, DEFAULT_FOLDER_PATH)

            main_category = path_parts[0] if path_parts else ""
            if self.use_date_subfolders and main_category in self.date_organization_categories:
                try:
                    mod_time = os.path.getmtime(source_file_path)
                    date_folder = datetime.fromtimestamp(mod_time).strftime('%Y-%m')
                    path_parts = path_parts + (date_folder,)
                except Exception as e:
                    self.progress.emit(f"  Warning: Could not get date for '{filename}'. Skipping date folder. Reason: {e}")

            target_folder_path = os.path.join(self.target_dir, *path_parts)

            try:
                os.makedirs(target_folder_path, exist_ok=True)
            except OSError as e:
                self.progress.emit(f"Error: Could not create folder '{'/'.join(path_parts)}'. Skipping '{filename}'. Reason: {e}")
                files_skipped_count += 1
                continue

            destination_file_path = os.path.join(target_folder_path, filename)
            counter = 1
            temp_filename = filename
            while os.path.exists(destination_file_path):
                temp_filename = f"{file_root}_{counter}{file_extension}"
                destination_file_path = os.path.join(target_folder_path, temp_filename)
                counter += 1
            
            if temp_filename != filename:
                self.progress.emit(f"  Note: Renaming '{filename}' to '{temp_filename}' due to a name conflict.")

            try:
                shutil.move(source_file_path, destination_file_path)
                display_path = os.path.join(*path_parts, temp_filename)
                self.progress.emit(f"Moved: '{filename}'  ->  '{display_path}'")
                files_moved_count += 1
            except Exception as e:
                self.progress.emit(f"Error: Could not move '{filename}'. Reason: {e}")
                files_skipped_count += 1
            
            # Update progress bar
            percent_complete = int(((i + 1) / total_files) * 100)
            self.progressBar.emit(percent_complete)

        self.finished.emit(files_moved_count, files_skipped_count)

    def stop(self):
        self.is_running = False


# Main GUI Window
class FileSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Sorter Pro")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.worker_thread = None
        self.sorter_worker = None

        self._create_widgets()
        self._create_layouts()
        self._connect_signals()
        self._set_initial_state()

    def _create_widgets(self):
        """Create all the UI widgets."""
        # Directory Selection
        self.dir_label = QLabel("Directory to Sort:")
        self.dir_path_edit = QLineEdit()
        self.dir_path_edit.setReadOnly(True)
        self.dir_path_edit.setPlaceholderText("Select a directory to organize...")
        self.browse_button = QPushButton("Browse...")

        # Configuration Options
        self.config_groupbox = QGroupBox("Options")
        self.use_date_checkbox = QCheckBox("Create date-based subfolders (e.g., 2023-10)")
        
        self.date_categories_label = QLabel("Apply date-based subfolders to these top-level categories:")
        self.date_categories_list = QListWidget()
        self.date_categories_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._populate_date_categories()

        # Action Buttons
        self.start_button = QPushButton("Start Sorting")
        
        # Log Output
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

    def _populate_date_categories(self):
        """Finds all unique top-level categories and adds them to the list widget."""
        top_level_categories = sorted(list(set(v[0] for v in FILE_TYPE_MAPPINGS.values())))
        for category in top_level_categories:
            item = QListWidgetItem(category)
            self.date_categories_list.addItem(item)
            if category in DEFAULT_DATE_ORGANIZATION_CATEGORIES:
                item.setSelected(True)

    def _create_layouts(self):
        """Arrange widgets in layouts."""
        # Directory selection layout
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path_edit)
        dir_layout.addWidget(self.browse_button)

        # Configuration layout
        config_layout = QVBoxLayout()
        config_layout.addWidget(self.use_date_checkbox)
        config_layout.addWidget(self.date_categories_label)
        config_layout.addWidget(self.date_categories_list)
        self.config_groupbox.setLayout(config_layout)

        # Main layout
        self.main_layout.addLayout(dir_layout)
        self.main_layout.addWidget(self.config_groupbox)
        self.main_layout.addWidget(self.start_button)
        self.main_layout.addWidget(QLabel("Log:"))
        self.main_layout.addWidget(self.log_output)
        self.main_layout.addWidget(self.progress_bar)

    def _connect_signals(self):
        """Connect widget signals to corresponding slots."""
        self.browse_button.clicked.connect(self.select_directory)
        self.dir_path_edit.textChanged.connect(self._update_start_button_state)
        self.start_button.clicked.connect(self.start_sorting)
        self.use_date_checkbox.stateChanged.connect(self._toggle_date_category_list)

    def _set_initial_state(self):
        """Set the initial state of widgets when the app starts."""
        self.start_button.setEnabled(False)
        self.use_date_checkbox.setChecked(DEFAULT_USE_DATE_SUBFOLDERS)
        self._toggle_date_category_list()
    
    def _update_start_button_state(self):
        """Enable start button only if a directory is selected."""
        self.start_button.setEnabled(bool(self.dir_path_edit.text()))
    
    def _toggle_date_category_list(self):
        """Enable or disable the date category list based on the checkbox."""
        is_checked = self.use_date_checkbox.isChecked()
        self.date_categories_label.setEnabled(is_checked)
        self.date_categories_list.setEnabled(is_checked)

    # --- SLOTS ---
    def select_directory(self):
        """Open a dialog to select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select a Directory to Sort")
        if directory:
            self.dir_path_edit.setText(directory)

    def start_sorting(self):
        """Prepare and start the background worker thread for sorting."""
        target_dir = self.dir_path_edit.text()
        use_date = self.use_date_checkbox.isChecked()
        selected_items = self.date_categories_list.selectedItems()
        date_categories = {item.text() for item in selected_items}

        self.log_output.clear()
        self.progress_bar.setValue(0)
        self._set_ui_enabled(False)

        # Create and start the worker thread
        self.worker_thread = QThread()
        self.sorter_worker = SorterWorker(target_dir, use_date, date_categories)
        self.sorter_worker.moveToThread(self.worker_thread)

        # Connect worker signals to GUI slots
        self.worker_thread.started.connect(self.sorter_worker.run)
        self.sorter_worker.finished.connect(self.worker_thread.quit)
        self.sorter_worker.finished.connect(self.sorter_worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.sorter_worker.progress.connect(self.update_log)
        self.sorter_worker.progressBar.connect(self.update_progress_bar)
        self.sorter_worker.finished.connect(self.sorting_finished)

        self.worker_thread.start()

    def update_log(self, message):
        """Append a message to the log window."""
        self.log_output.appendPlainText(message)

    def update_progress_bar(self, value):
        """Update the progress bar's value."""
        self.progress_bar.setValue(value)

    def sorting_finished(self, files_moved, files_skipped):
        """Handle cleanup and feedback after sorting is complete."""
        self.log_output.appendPlainText("\n--- File sorting complete ---")
        self.log_output.appendPlainText(f"Total files moved: {files_moved}")
        self.log_output.appendPlainText(f"Total files skipped: {files_skipped}")
        self._set_ui_enabled(True)

    def _set_ui_enabled(self, is_enabled):
        """Enable or disable UI elements during processing."""
        self.browse_button.setEnabled(is_enabled)
        self.config_groupbox.setEnabled(is_enabled)
        self.start_button.setEnabled(is_enabled)
        if is_enabled:
            self._update_start_button_state() # Re-check if dir is selected
    
    def closeEvent(self, event):
        """Ensure the worker thread is stopped if the window is closed."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.sorter_worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait() # Wait for the thread to finish
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSorterApp()
    window.show()
    sys.exit(app.exec())