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
    def __init__(self, image_object, scaled_width, canvas_rect):
        super().__init__()
        self.image_object = image_object
        self.canvas_rect = canvas_rect
        self.pixmap = QPixmap(image_object.image_path)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setPos(QPointF(-scaled_width / 2, -scaled_width / 2))
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
            if self.canvas_rect.contains(new_pos):
                self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_being_dragged = False

class Sidebar(QListWidget):
    addItemToCanvas = pyqtSignal(MyImage)

    def __init__(self, sidebar_height):
        super().__init__()
        self.setIconSize(QSize(150, 150))
        self.setMaximumHeight(sidebar_height)

    def add_item(self, image_object):
        sidebar_item = QListWidgetItem()
        sidebar_item.setIcon(QIcon(image_object.image_path))
        sidebar_item.setText(image_object.name)
        sidebar_item.image_object = image_object  # Store the image object as an attribute
        self.addItem(sidebar_item)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            image_object = item.image_object
            self.addItemToCanvas.emit(image_object)

class Canvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setSceneRect(QRectF(-300, -200, 600, 400))  # Adjust as needed

    def addItemToCanvas(self, image_object):
        scaled_width = 100
        pixmap_item = DraggablePixmapObject(image_object, scaled_width, self.sceneRect())
        self.scene().addItem(pixmap_item)

class GUI(QMainWindow):
    def __init__(self, objects):
        super().__init__()
        self.setWindowTitle("Soundscape")
        self.setGeometry(100, 100, 800, 600)  # Adjust the window size as needed

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        canvas = Canvas()
        sidebar_height = 200
        sidebar = Sidebar(sidebar_height)

        layout.addWidget(canvas)
        layout.addWidget(sidebar)

        sidebar.addItemToCanvas.connect(canvas.addItemToCanvas)

        for key in objects:
            image_object = objects[key]
            sidebar.add_item(image_object)



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
