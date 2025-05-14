from backend.api import BitcioAPI
from backend.trader import Scalper
from frontend.ui import ScalpingApp
from config import API_KEY, API_SECRET
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    api = BitcioAPI(API_KEY, API_SECRET)
    scalper = Scalper(api)

    app = QApplication(sys.argv)
    gui = ScalpingApp(scalper)
    sys.exit(app.exec_())