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

SAVE_PATH = "data"  # The save path (right now used for progress)

def load_flashcards():
    if os.path.exists(FLASHCARD_FILE):
        with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    file = open(SAVE_PATH, "w") #opens the file with write access
    file.write(json.dumps(data)) #writes the configs as string
    file.close() #closes file

def load_data():
     if os.path.exists(SAVE_PATH):
         file = open(SAVE_PATH)
         data = file.read()
         return json.loads(data)

class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.flashcards = load_flashcards()
        
        self.data = {   # Datat can contain anything, that should be saved between sessions
            "card_index": 0,
            "review_list": [],
        }
        
        loaded_data = load_data()
        if loaded_data:
            self.data = loaded_data

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
        if not self.data["review_list"]: # only shuffle when we arent resuming
            self.data["review_list"] = list(self.flashcards)  # copy in order
            random.shuffle(self.data["review_list"]) # Rnadom order to avoid learnign by pattern
        
        self.showing_answer = False
        self.start_btn.setEnabled(False)
        self.show_answer_btn.setEnabled(True)
        self.next_c_btn.setEnabled(True)
        self.next_f_btn.setEnabled(True)
        self.prev_btn.setEnabled(True)
        self.show_card()

    def show_card(self):
        if self.data["card_index"] < len(self.data["review_list"]):
            card = self.data["review_list"][self.data["card_index"]]
            if self.showing_answer:
                display = f"Q: {card['question']}\n\nA: {card['answer']}"
            else:
                display = f"Q: {card['question']}"
            self.card_label.setText(display)

            # Update the progress label
            self.progress_label.setText(f"Progress: {self.data["card_index"] + 1} of {len(self.data["review_list"])}")
        else:
            self.card_label.setText("🎉 You've finished all flashcards!")
            self.show_answer_btn.setEnabled(False)
            self.next_c_btn.setEnabled(False)
            self.next_f_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.data["review_list"] = [] # Reset when done, so that it gets reshuffled next time
            self.data["card_index"] = 0
        save_data(self.data) #Save everything we update card

    def show_answer(self):
        self.showing_answer = True
        self.show_card()

    def next_card_continue(self):
        if self.data["card_index"] < len(self.data["review_list"]) - 1:
            self.data["card_index"] += 1
            self.showing_answer = False
            self.show_card()
        else:
            self.data["card_index"] += 1
            self.show_card()

    def next_card_fail(self):
        if self.data["card_index"] < len(self.data["review_list"]):
            card = self.data["review_list"][self.data["card_index"]]

            # Insert the card between 3 and 10 positions ahead
            insert_index = min(random.randrange(self.data["card_index"] + 3, self.data["card_index"] + 10), len(self.data["review_list"]))

            self.data["review_list"].insert(insert_index, card)
        self.next_card_continue()

    def prev_card(self):
        if self.data["card_index"] > 0:
            self.data["card_index"] -= 1
            self.showing_answer = False
            self.show_card()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())