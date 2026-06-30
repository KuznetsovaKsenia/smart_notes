"""Smart Notes desktop application.

A simple PyQt5 app for creating notes and assigning tags.
Notes are stored locally in notes.json near this file.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

NOTES_FILE = Path(__file__).with_name("notes.json")


def load_notes() -> Dict[str, dict]:
    """Load notes from notes.json. If file does not exist, create empty storage."""
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("{}", encoding="utf-8")
        return {}

    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        QMessageBox.warning(
            None,
            "Ошибка чтения файла",
            "Файл notes.json поврежден. Будет создан пустой список заметок.",
        )
        return {}


def save_notes(notes: Dict[str, dict]) -> None:
    """Save notes to notes.json."""
    NOTES_FILE.write_text(
        json.dumps(notes, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


class SmartNotes(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.notes = load_notes()
        self.setup_ui()
        self.refresh_notes_list()

    def setup_ui(self) -> None:
        self.setWindowTitle("Умные заметки")
        self.resize(900, 600)

        self.text = QTextEdit()
        self.notes_label = QLabel("Список заметок")
        self.tags_label = QLabel("Список тегов")
        self.notes_list = QListWidget()
        self.tags_list = QListWidget()
        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("Введите тег для поиска")

        self.add_note_button = QPushButton("Добавить заметку")
        self.delete_note_button = QPushButton("Удалить заметку")
        self.save_note_button = QPushButton("Сохранить заметку")
        self.add_tag_button = QPushButton("Добавить тег")
        self.delete_tag_button = QPushButton("Удалить тег")
        self.search_button = QPushButton("Искать заметку по тегу")

        self.notes_list.itemClicked.connect(self.show_note)
        self.add_note_button.clicked.connect(self.add_note)
        self.delete_note_button.clicked.connect(self.delete_note)
        self.save_note_button.clicked.connect(self.save_current_note)
        self.add_tag_button.clicked.connect(self.add_tag)
        self.delete_tag_button.clicked.connect(self.delete_tag)
        self.search_button.clicked.connect(self.search_by_tag)

        main_layout = QHBoxLayout()
        side_layout = QVBoxLayout()
        note_buttons_layout = QHBoxLayout()
        tag_buttons_layout = QHBoxLayout()

        note_buttons_layout.addWidget(self.add_note_button)
        note_buttons_layout.addWidget(self.delete_note_button)
        tag_buttons_layout.addWidget(self.add_tag_button)
        tag_buttons_layout.addWidget(self.delete_tag_button)

        side_layout.addWidget(self.notes_label)
        side_layout.addWidget(self.notes_list)
        side_layout.addLayout(note_buttons_layout)
        side_layout.addWidget(self.save_note_button)
        side_layout.addWidget(self.tags_label)
        side_layout.addWidget(self.tags_list)
        side_layout.addWidget(self.search_line)
        side_layout.addLayout(tag_buttons_layout)
        side_layout.addWidget(self.search_button)

        main_layout.addWidget(self.text, stretch=2)
        main_layout.addLayout(side_layout, stretch=1)
        self.setLayout(main_layout)

    def selected_note_name(self) -> Optional[str]:
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Нет выбранной заметки", "Сначала выберите заметку.")
            return None
        return selected_items[0].text()

    def refresh_notes_list(self, notes_to_show: Optional[Dict[str, dict]] = None) -> None:
        self.notes_list.clear()
        self.tags_list.clear()
        self.text.clear()
        source = notes_to_show if notes_to_show is not None else self.notes
        self.notes_list.addItems(source.keys())

    def show_note(self, _item=None) -> None:
        note_name = self.selected_note_name()
        if note_name is None:
            return
        note = self.notes[note_name]
        self.text.setText(note.get("content", ""))
        self.tags_list.clear()
        self.tags_list.addItems(note.get("tags", []))

    def add_note(self) -> None:
        note_name, ok = QInputDialog.getText(self, "Добавление заметки", "Введите название заметки")
        note_name = note_name.strip()

        if not ok or not note_name:
            return
        if note_name in self.notes:
            QMessageBox.warning(self, "Такая заметка уже есть", "Заметка с таким названием уже существует.")
            return

        self.notes[note_name] = {"content": "", "tags": []}
        save_notes(self.notes)
        self.refresh_notes_list()

    def delete_note(self) -> None:
        note_name = self.selected_note_name()
        if note_name is None:
            return

        del self.notes[note_name]
        save_notes(self.notes)
        self.refresh_notes_list()

    def save_current_note(self) -> None:
        note_name = self.selected_note_name()
        if note_name is None:
            return

        self.notes[note_name]["content"] = self.text.toPlainText()
        save_notes(self.notes)
        QMessageBox.information(self, "Сохранено", "Заметка сохранена.")

    def add_tag(self) -> None:
        note_name = self.selected_note_name()
        if note_name is None:
            return

        tag_name, ok = QInputDialog.getText(self, "Добавление тега", "Введите новый тег")
        tag_name = tag_name.strip().lower()

        if not ok or not tag_name:
            return

        tags = self.notes[note_name].setdefault("tags", [])
        if tag_name not in tags:
            tags.append(tag_name)
            save_notes(self.notes)
            self.show_note()

    def delete_tag(self) -> None:
        note_name = self.selected_note_name()
        if note_name is None:
            return

        selected_tags = self.tags_list.selectedItems()
        if not selected_tags:
            QMessageBox.information(self, "Нет выбранного тега", "Сначала выберите тег.")
            return

        tag_name = selected_tags[0].text()
        self.notes[note_name]["tags"].remove(tag_name)
        save_notes(self.notes)
        self.show_note()

    def search_by_tag(self) -> None:
        if self.search_button.text() == "Искать заметку по тегу":
            tag = self.search_line.text().strip().lower()
            if not tag:
                QMessageBox.information(self, "Пустой тег", "Введите тег для поиска.")
                return

            filtered_notes = {
                name: note
                for name, note in self.notes.items()
                if tag in note.get("tags", [])
            }
            self.refresh_notes_list(filtered_notes)
            self.search_button.setText("Сброс фильтра")
        else:
            self.search_button.setText("Искать заметку по тегу")
            self.search_line.clear()
            self.refresh_notes_list()


def main() -> None:
    app = QApplication([])
    window = SmartNotes()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
