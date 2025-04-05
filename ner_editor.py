import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QListWidget, QMessageBox, QScrollArea, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class WordButton(QPushButton):
    def __init__(self, text, index):
        super().__init__(text)
        self.index = index
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #999;
                padding: 2px;
                margin: 1px;
                border-radius: 3px;
                min-width: 50px;
            }
            QPushButton:checked {
                background-color: #ffd700;
            }
        """
        )

class NEREditor(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.current_index = 0
        self.selected_start = None
        self.colors = {}
        self.init_ui()
        self.load_current_example()

    def init_ui(self):
        self.setWindowTitle('NER Annotation Editor')
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton('← Previous')
        self.prev_btn.clicked.connect(self.prev_example)
        self.next_btn = QPushButton('Next →')
        self.next_btn.clicked.connect(self.next_example)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        scroll = QScrollArea()
        self.text_container = QWidget()
        self.text_layout = QGridLayout(self.text_container)  # Используем таблицу для компактности
        self.text_layout.setContentsMargins(2, 2, 2, 2)
        scroll.setWidget(self.text_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        control_layout = QHBoxLayout()
        
        self.ner_list = QListWidget()
        self.ner_list.itemDoubleClicked.connect(self.remove_entity)
        control_layout.addWidget(self.ner_list)

        right_panel = QVBoxLayout()
        self.label_combo = QComboBox()
        self.update_label_combo()
        
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter new label or select")
        right_panel.addWidget(QLabel('Entity Type:'))
        right_panel.addWidget(self.label_combo)
        right_panel.addWidget(self.label_input)

        self.add_btn = QPushButton('Add Entity')
        self.add_btn.clicked.connect(self.confirm_entity)
        right_panel.addWidget(self.add_btn)

        self.save_btn = QPushButton('Save All Changes')
        self.save_btn.clicked.connect(self.save_changes)
        right_panel.addWidget(self.save_btn)

        control_layout.addLayout(right_panel)
        layout.addLayout(control_layout)

    def update_label_combo(self):
        all_labels = set()
        for item in self.data:
            all_labels.update(item['label'])
        self.label_combo.clear()
        self.label_combo.addItems(sorted(all_labels))

    def load_current_example(self):
        example = self.data[self.current_index]
        
        for i in reversed(range(self.text_layout.count())): 
            self.text_layout.itemAt(i).widget().deleteLater()
        
        self.word_buttons = []
        row, col = 0, 0
        for idx, word in enumerate(example['tokenized_text']):
            btn = WordButton(word, idx)
            btn.clicked.connect(self.on_word_click)
            self.word_buttons.append(btn)
            self.text_layout.addWidget(btn, row, col)
            col += 1
            if col > 7:  # Перенос на новую строку
                col = 0
                row += 1

        self.color_map = {}
        for ner in example['ner']:
            start, end, label = ner
            color = self.get_color_for_label(label)
            for i in range(start, end+1):
                self.word_buttons[i].setStyleSheet(f"background-color: {color};")

        self.ner_list.clear()
        for ner in example['ner']:
            start, end, label = ner
            text = ' '.join(example['tokenized_text'][start:end+1])
            self.ner_list.addItem(f"{label}: [{start}-{end}] {text}")

    def get_color_for_label(self, label):
        if label not in self.colors:
            color = QColor()
            color.setHsv((len(self.colors) * 70) % 360, 150, 230)
            self.colors[label] = color.name()
        return self.colors[label]

    def on_word_click(self):
        clicked_btn = self.sender()
        index = clicked_btn.index
        
        if self.selected_start is None:
            self.clear_selection()
            self.selected_start = index
            clicked_btn.setChecked(True)
        else:
            self.selected_end = index
            self.show_selection_area()

    def clear_selection(self):
        for btn in self.word_buttons:
            btn.setChecked(False)
        self.selected_start = None
        self.selected_end = None

    def show_selection_area(self):
        start = min(self.selected_start, self.selected_end)
        end = max(self.selected_start, self.selected_end)
        
        for i in range(start, end+1):
            self.word_buttons[i].setChecked(True)

    def confirm_entity(self):
        if self.selected_start is None or self.selected_end is None:
            return
        
        start = min(self.selected_start, self.selected_end)
        end = max(self.selected_start, self.selected_end)
        label = self.label_input.text().strip() or self.label_combo.currentText()
        
        if not label:
            QMessageBox.warning(self, "Error", "Please enter or select a label")
            return

        self.data[self.current_index]['ner'].append([start, end, label])
        
        self.load_current_example()
        self.clear_selection()

    def remove_entity(self, item):
        row = self.ner_list.row(item)
        del self.data[self.current_index]['ner'][row]
        self.load_current_example()

    def prev_example(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_example()

    def next_example(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.load_current_example()

    def save_changes(self):
        with open('output/annotated_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, 'Saved', 'All changes saved to annotated_data.json')

if __name__ == '__main__':
    with open('output/gliner.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    app = QApplication(sys.argv)
    editor = NEREditor(data)
    editor.show()
    sys.exit(app.exec_())
