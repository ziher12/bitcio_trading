from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import os
import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # API ключи
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setText(config.API_KEY)
        self.api_secret_input = QLineEdit(self)
        self.api_secret_input.setText(config.API_SECRET)
        self.api_secret_input.setEchoMode(QLineEdit.Password)

        # Торговые параметры
        self.max_position_input = QLineEdit(self)
        self.max_position_input.setText(str(config.MAX_POSITION))
        self.min_spread_input = QLineEdit(self)
        self.min_spread_input.setText(str(config.MIN_SPREAD))
        self.auto_duration_input = QLineEdit(self)
        self.auto_duration_input.setText(str(config.AUTO_SCALP_DURATION))

        # Макет
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key_input)
        layout.addWidget(QLabel("API Secret:"))
        layout.addWidget(self.api_secret_input)
        layout.addWidget(QLabel("Макс. позиция (доля баланса):"))
        layout.addWidget(self.max_position_input)
        layout.addWidget(QLabel("Мин. спред:"))
        layout.addWidget(self.min_spread_input)
        layout.addWidget(QLabel("Длительность авто-скальпинга (сек):"))
        layout.addWidget(self.auto_duration_input)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить", self)
        cancel_button = QPushButton("Отмена", self)
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_settings(self):
        """Сохранение настроек."""
        try:
            # Обновление переменных окружения
            os.environ['BITCIO_API_KEY'] = self.api_key_input.text()
            os.environ['BITCIO_API_SECRET'] = self.api_secret_input.text()

            # Обновление config.py
            config.API_KEY = self.api_key_input.text()
            config.API_SECRET = self.api_secret_input.text()
            config.MAX_POSITION = float(self.max_position_input.text())
            config.MIN_SPREAD = float(self.min_spread_input.text())
            config.AUTO_SCALP_DURATION = int(self.auto_duration_input.text())

            QMessageBox.information(self, "Успех", "Настройки сохранены")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")