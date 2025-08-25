import sys
import json
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt

FLASHCARD_FILE = "flashcards.json"

def load_flashcards():
    if os.path.exists(FLASHCARD_FILE):
        with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.flashcards = load_flashcards()
        self.card_index = 0
        self.showing_answer = False

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel#CardLabel {
                background-color: #ffffff;
                border: 2px solid #555;
                border-radius: 15px;
                padding: 30px;
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.card_label = QLabel("Click 'Start Review'")
        self.card_label.setObjectName("CardLabel")
        self.card_label.setAlignment(Qt.AlignTop)
        self.card_label.setWordWrap(True)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.card_label)
        self.scroll_area.setFixedHeight(250)

        self.layout.addWidget(self.scroll_area)

        # Progress label
        self.progress_label = QLabel("Progress: 0 of 0")
        self.layout.addWidget(self.progress_label)

        # Buttons
        self.button_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_card)
        self.prev_btn.setEnabled(False)

        self.next_c_btn = QPushButton("Next (C)")
        self.next_c_btn.clicked.connect(self.next_card_continue)
        self.next_c_btn.setEnabled(False)

        self.next_f_btn = QPushButton("Next (F)")
        self.next_f_btn.clicked.connect(self.next_card_fail)
        self.next_f_btn.setEnabled(False)

        self.show_answer_btn = QPushButton("Show Answer")
        self.show_answer_btn.clicked.connect(self.show_answer)
        self.show_answer_btn.setEnabled(False)

        self.start_btn = QPushButton("Start Review")
        self.start_btn.clicked.connect(self.start_review)

        self.button_layout.addWidget(self.prev_btn)
        self.button_layout.addWidget(self.start_btn)
        self.button_layout.addWidget(self.show_answer_btn)
        self.button_layout.addWidget(self.next_c_btn)
        self.button_layout.addWidget(self.next_f_btn)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def start_review(self):
        if not self.flashcards:
            QMessageBox.information(self, "No Cards", "No flashcards found!")
            return
        self.review_list = list(self.flashcards)  # copy in order
        random.shuffle(self.review_list)
        self.card_index = 0
        self.showing_answer = False
        self.start_btn.setEnabled(False)
        self.show_answer_btn.setEnabled(True)
        self.next_c_btn.setEnabled(True)
        self.next_f_btn.setEnabled(True)
        self.prev_btn.setEnabled(True)
        self.show_card()

    def show_card(self):
        if self.card_index < len(self.review_list):
            card = self.review_list[self.card_index]
            if self.showing_answer:
                display = f"Q: {card['question']}\n\nA: {card['answer']}"
            else:
                display = f"Q: {card['question']}"
            self.card_label.setText(display)

            # Update the progress label
            self.progress_label.setText(f"Progress: {self.card_index + 1} of {len(self.review_list)}")
        else:
            self.card_label.setText("🎉 You've finished all flashcards!")
            self.show_answer_btn.setEnabled(False)
            self.next_c_btn.setEnabled(False)
            self.next_f_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.start_btn.setEnabled(True)

    def show_answer(self):
        self.showing_answer = True
        self.show_card()

    def next_card_continue(self):
        if self.card_index < len(self.review_list) - 1:
            self.card_index += 1
            self.showing_answer = False
            self.show_card()
        else:
            self.card_index += 1
            self.show_card()

    def next_card_fail(self):
        if self.card_index < len(self.review_list):
            card = self.review_list[self.card_index]

            # Insert the card 6 positions ahead
            insert_index = min(self.card_index + 6, len(self.review_list))

            self.review_list.insert(insert_index, card)

        self.next_card_continue()

    def prev_card(self):
        if self.card_index > 0:
            self.card_index -= 1
            self.showing_answer = False
            self.show_card()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())