import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QGraphicsView, QGraphicsScene,
                             QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGraphicsLineItem)
from PyQt5.QtCore import Qt, QLineF, QPointF, QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont

from data_structures.Attribute import Attribute
from data_structures.Entity import Entity
from data_structures.Relationship import Relationship


class PositionNotifier(QObject):
    positionChanged = pyqtSignal()


def parse_code(code: str):
    entities = []
    relationships = []
    lines: list[str] = code.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#Entity '):
            entity = Entity(line[len('#Entity '):])
            i += 1
            attrs = []
            while i < len(lines) and lines[i].startswith('\t'):
                attr_line = lines[i].strip()
                if attr_line:
                    is_primary = attr_line.startswith('<u>') and attr_line.endswith('</u>')
                    attr = attr_line[3:-4] if is_primary else attr_line
                    attrs.append(Attribute(attr, is_primary))
                i += 1
            entity.attributes = attrs
            entities.append(entity)
        elif line.startswith('#Relation '):
            rel = Relationship(line[len('#Relation '):])
            i += 1
            rel_lines = []
            while i < len(lines) and lines[i].startswith('\t'):
                rel_line = lines[i][1:]
                if rel_line:
                    rel_lines.append(rel_line)
                i += 1
            entities_part = []
            cardinalities_part = []
            attributes_part = []
            step = 0
            for line in rel_lines:
                if line.startswith('['):
                    step = 1
                    cardinalities_part.append(line.strip('[]'))
                elif step == 0:
                    entities_part.append(line)
                elif step == 1 and len(cardinalities_part) < len(entities_part):
                    cardinalities_part.append(line.strip('[]'))
                else:
                    is_primary = line.startswith('<u>') and line.endswith('</u>')
                    attributes_part.append(Attribute(line, is_primary))
            rel.entities = entities_part
            rel.cardinalities = []
            for c in cardinalities_part:
                parts = c.split(',')
                if len(parts) == 2:
                    rel.cardinalities.append((parts[0].strip(), parts[1].strip()))
            rel.attributes = attributes_part
            relationships.append(rel)
            i += 1
        elif line == "":
            i += 1
        else:
            raise "Wrong code"
    return entities, relationships


class PositionManager:
    def __init__(self):
        self.positions = {"entities": {}, "relationships": {}}

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                self.positions = json.load(f)
        except FileNotFoundError:
            pass

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.positions, f)

    def update_entity_position(self, name, x, y):
        self.positions["entities"][name] = {"x": x, "y": y}

    def update_relationship_position(self, name, x, y):
        self.positions["relationships"][name] = {"x": x, "y": y}

    def get_entity_position(self, name):
        pos = self.positions["entities"].get(name, {"x": 0, "y": 0})
        return pos["x"], pos["y"]

    def get_relationship_position(self, name):
        pos = self.positions["relationships"].get(name, {"x": 0, "y": 0})
        return pos["x"], pos["y"]


class EntityItem(QGraphicsRectItem):
    def __init__(self, entity, pos_manager):
        super().__init__()
        self.entity = entity
        self.pos_manager = pos_manager
        self.notifier = PositionNotifier()
        x, y = pos_manager.get_entity_position(entity.name)
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsScenePositionChanges)
        self.setBrush(QBrush(Qt.white))
        self.update_rect()

    def update_rect(self):
        attr_height = 20
        header_height = 30
        num_attrs = len(self.entity.attributes)
        rect_width = 150
        rect_height = header_height + num_attrs * attr_height
        self.setRect(0, 0, rect_width, rect_height)

        for child in self.childItems():
            if isinstance(child, QGraphicsTextItem):
                self.scene().removeItem(child)

        header = QGraphicsTextItem(self.entity.name, self)
        header.setPos(5, 5)
        y_pos = header_height
        for attr in self.entity.attributes:
            attr, is_primary = attr.name, attr.is_primary
            text = QGraphicsTextItem(self)
            if is_primary:
                text.setHtml(f"<u>{attr}</u>")
            else:
                text.setPlainText(attr)
            text.setPos(5, y_pos)
            y_pos += attr_height

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.pos_manager.update_entity_position(self.entity.name, self.scenePos().x(), self.scenePos().y())
            self.notifier.positionChanged.emit()
        return super().itemChange(change, value)


class RelationshipItem(QGraphicsEllipseItem):
    def __init__(self, relationship, pos_manager):
        super().__init__()
        self.relationship = relationship
        self.pos_manager = pos_manager
        self.notifier = PositionNotifier()
        x, y = pos_manager.get_relationship_position(relationship.name)
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsScenePositionChanges)
        self.setBrush(QBrush(QColor(200, 200, 255)))
        self.setRect(0, 0, 100, 60)
        self.text = QGraphicsTextItem(relationship.name, self)
        self.text.setPos(10, 20)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.pos_manager.update_relationship_position(self.relationship.name, self.scenePos().x(),
                                                          self.scenePos().y())
            self.notifier.positionChanged.emit()
        return super().itemChange(change, value)


class LineItem(QGraphicsLineItem):
    def __init__(self, source, target, cardinality):
        super().__init__()
        self.source = source
        self.target = target
        self.cardinality = cardinality
        self.label = QGraphicsTextItem(cardinality, self)
        self.label.setFont(QFont("Arial", 10))
        self.update_line()
        source.notifier.positionChanged.connect(self.update_line)
        if isinstance(target, RelationshipItem):
            target.notifier.positionChanged.connect(self.update_line)
        else:
            target.notifier.positionChanged.connect(self.update_line)

    def update_line(self):
        start = self.source.scenePos() + QPointF(self.source.rect().width() / 2, self.source.rect().height() / 2)
        end = self.target.scenePos() + QPointF(self.target.rect().width() / 2, self.target.rect().height() / 2)
        self.setLine(QLineF(start, end))
        mid = (start + end) / 2 - QPointF(20, 0)
        self.label.setPos(mid)


class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source):
        if source.hasText():
            cursor = self.textCursor()
            cursor.insertText(source.text())
            self.setTextCursor(cursor)


class ERDiagramApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pos_manager = PositionManager()
        self.entities = []
        self.relationships = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("ER Diagram Tool")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        layout = QHBoxLayout()

        self.text_edit = PlainTextEdit()
        self.text_edit.setPlaceholderText("Enter ER diagram code here...")
        layout.addWidget(self.text_edit, 1)

        right_layout = QVBoxLayout()
        self.generate_btn = QPushButton("Generate Diagram")
        self.generate_btn.clicked.connect(self.generate_diagram)
        right_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("Save Positions")
        self.save_btn.clicked.connect(self.save_positions)
        right_layout.addWidget(self.save_btn)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        right_layout.addWidget(self.view)

        layout.addLayout(right_layout, 2)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate_diagram(self):
        self.scene.clear()
        try:
            self.entities, self.relationships = parse_code(self.text_edit.toPlainText())
        except BaseException as e:
            return
        self.pos_manager.load("positions.json")

        entity_items = {}
        for entity in self.entities:
            item = EntityItem(entity, self.pos_manager)
            self.scene.addItem(item)
            entity_items[entity.name] = item

        for rel in self.relationships:
            rel_item = RelationshipItem(rel, self.pos_manager)
            self.scene.addItem(rel_item)
            for i, entity_name in enumerate(rel.entities):
                entity = next(e for e in self.entities if e.name == entity_name)
                source = entity_items[entity.name]
                target = rel_item
                cardinality = f"[{rel.cardinalities[i][0]},{rel.cardinalities[i][1]}]"
                line = LineItem(source, target, cardinality)
                self.scene.addItem(line)

    def save_positions(self):
        self.pos_manager.save("positions.json")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ERDiagramApp()
    window.show()
    sys.exit(app.exec_())
