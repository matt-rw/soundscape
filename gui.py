import sys

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (QApplication, QGraphicsObject, QGraphicsScene,
                             QGraphicsView, QListWidget, QListWidgetItem,
                             QMainWindow, QPushButton, QVBoxLayout, QWidget)


class MyImage:
    def __init__(self, image_id, image_path):
        self.image_id = image_id
        self.image_path = image_path
        self.name = image_path.split('/')[-1].split('.')[0]

class DraggablePixmapObject(QGraphicsObject):
    def __init__(self, image: MyImage):
        super().__init__()
        self.image = image
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
        TOP = -250 + 18
        BOTTOM = 200 - 18
        LEFT = -400 + 13
        RIGHT = 350 - 13
        if self.is_being_dragged:
            new_pos = event.scenePos() + self.offset
            if (LEFT <= new_pos.x() <= RIGHT) and (TOP <= new_pos.y() <= BOTTOM):
                self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_being_dragged = False

class Bottombar(QListWidget):
    addItemToCanvas = pyqtSignal(MyImage)

    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(150, 150))
        self.setMaximumHeight(100)

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
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(-300, -200, 600, 400)
        self.resize(600, 400)
        self.setSceneRect(rect)

    def addItemToCanvas(self, image):
        pixmap_item = DraggablePixmapObject(image)
        self.scene().addItem(pixmap_item)

class GUI(QMainWindow):
    def __init__(self, objects):
        super().__init__()
        self.setWindowTitle("Soundscape")
        #self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        canvas = Canvas()
        layout.addWidget(canvas)

        bottombar = Bottombar()
        layout.addWidget(bottombar)

        bottombar.addItemToCanvas.connect(canvas.addItemToCanvas)

        for image in objects:
            bottombar.add_item(objects[image])



if __name__ == "__main__":
    # Example objects
    objects = {
        "armadillo": MyImage(1, "files/armadillo/armadillo.png"),
        "thunder": MyImage(2, "files/thunder/thunder.png"),
    }

    app = QApplication(sys.argv)
    gui = GUI(objects)
    gui.show()
    sys.exit(app.exec())
