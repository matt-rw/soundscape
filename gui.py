import sys
import os
import logging
import multiprocessing

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (QApplication, QGraphicsObject, QGraphicsScene,
                             QGraphicsView, QListWidget, QListWidgetItem,
                             QMainWindow, QPushButton, QVBoxLayout, QWidget)
from pygame import mixer_music

from mixer import MySound, MyMixer


os.environ['QT_LOGGING_RULES'] = 'qt. *=false'


TOP = -250 + 18
BOTTOM = 200 - 18
LEFT = -400 + 13
RIGHT = 350 - 13

class MyImage:
    def __init__(self, image_path):
        self.image_path = image_path
        self.name = image_path.split('/')[-1].split('.')[0]

class DraggablePixmapObject(QGraphicsObject):
    def __init__(self, image: MyImage, image_id: int):
        super().__init__()
        self.id = image_id
        self.name = image.name
        self.pixmap = QPixmap(image.image_path).scaled(50, 50)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setPos(QPointF(-self.pixmap.width() / 2, -self.pixmap.height() / 2))
        self.is_being_dragged = False
        self.offset = QPointF(0, 0)

    def boundingRect(self):
        return QRectF(self.pixmap.rect())

    def paint(self, painter, option, widget):
        painter.drawPixmap(QPointF(0, 0), self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_being_dragged = True
            self.offset = self.pos() - event.scenePos()

    def mouseMoveEvent(self, event):
        if self.is_being_dragged:
            new_pos = event.scenePos() + self.offset
            if (LEFT <= new_pos.x() <= RIGHT) and (TOP <= new_pos.y() <= BOTTOM):
                self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_being_dragged = False


class Bottombar(QListWidget):
    addItemToCanvas = pyqtSignal(MyImage)

    def __init__(self, images):
        super().__init__()
        self.setIconSize(QSize(150, 150))
        self.setMaximumHeight(100)
        for image in images:
            self.add_item(image)

    def add_item(self, image):
        item = QListWidgetItem()
        item.setIcon(QIcon(image.image_path))
        item.setText(image.name)
        item.image = image
        self.addItem(item)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            self.addItemToCanvas.emit(item.image)

class Canvas(QGraphicsView):
    def __init__(self, mixer):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(-300, -200, 600, 400)
        self.resize(600, 400)
        self.setSceneRect(rect)

        # pass mixer to add channels
        self.mixer = mixer

    def addItemToCanvas(self, image: MyImage):
        item = DraggablePixmapObject(image, 0)
        self.scene().addItem(item)

        # initialize sound object and add channel
        name = item.name
        mp3 = f'files/{name}/{name}.mp3'
        location = item.x(), item.y()
        interval = (5, 10)
        sound = MySound(mp3, location, interval)
        self.mixer.add_channel(sound)

class GUI(QMainWindow):
    def __init__(self, objects):
        super().__init__()
        self.setWindowTitle("Soundscape")
        # dynamic sizing
        # self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.playbutton = QPushButton()
        self.playbutton.setIcon(QIcon('gui-images/play-32.png'))
        self.playbutton.setIconSize(QSize(12,12))
        self.playbutton.setMaximumSize(25,35)
        self.playbutton.clicked.connect(self.toggle_play)
        layout.addWidget(self.playbutton, alignment=Qt.AlignmentFlag.AlignRight)
        self.playing = False
        # run mixer
        self.mixer = MyMixer()

        self.canvas = Canvas(self.mixer)
        layout.addWidget(self.canvas)

        self.bottombar = Bottombar(objects)
        layout.addWidget(self.bottombar)
        self.bottombar.addItemToCanvas.connect(self.canvas.addItemToCanvas)


    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.playbutton.setIcon(QIcon('gui-images/pause-32.png'))
            self.mixer.play()
        else:
            self.playbutton.setIcon(QIcon('gui-images/play-32.png'))
            self.mixer.pause()


    def mixer_init(self, event_play, event_pause):
        while True:
            event_play.wait()
            event_play.clear()

            if event_pause.is_set():
                event_pause.clear()
                continue


    def remove_channel(self, item: DraggablePixmapObject):
        pass


if __name__ == "__main__":
    # Example objects
    images = []
    path = 'files'
    for img in os.listdir(path):
        if img != '.DS_Store':
            image_file = f'{path}/{img}/{img}.png'
            image = MyImage(image_file)
            images.append(image)

    app = QApplication(sys.argv)
    gui = GUI(images)
    gui.show()
    sys.exit(app.exec())
