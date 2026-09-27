"""
generate_icon.py - Creates app_icon.ico using PyQt6 QPainter
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt

def make_icon():
    app = QApplication(sys.argv)
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Sleek dark acrylic background
    painter.setBrush(QBrush(QColor(24, 28, 38)))
    painter.setPen(QPen(QColor(0, 120, 212), 8))
    painter.drawRoundedRect(12, 12, 232, 232, 48, 48)

    # Glowing keyboard chiclets
    painter.setBrush(QBrush(QColor(0, 120, 212)))
    painter.setPen(Qt.PenStyle.NoPen)
    
    # Top keys
    painter.drawRoundedRect(36, 44, 40, 40, 10, 10)
    painter.drawRoundedRect(88, 44, 40, 40, 10, 10)
    painter.drawRoundedRect(140, 44, 40, 40, 10, 10)
    painter.drawRoundedRect(192, 44, 28, 40, 10, 10)

    # Middle keys
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.drawRoundedRect(36, 96, 52, 40, 10, 10)
    painter.drawRoundedRect(100, 96, 40, 40, 10, 10)
    painter.drawRoundedRect(152, 96, 68, 40, 10, 10)

    # Bottom keys & Spacebar
    painter.setBrush(QBrush(QColor(0, 120, 212)))
    painter.drawRoundedRect(36, 148, 40, 40, 10, 10)
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.drawRoundedRect(88, 148, 80, 40, 10, 10)
    painter.setBrush(QBrush(QColor(0, 120, 212)))
    painter.drawRoundedRect(180, 148, 40, 40, 10, 10)

    painter.end()
    pixmap.save("app_icon.ico", "ICO")
    print("app_icon.ico generated successfully!")

if __name__ == "__main__":
    make_icon()
