from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import copy, math

class EItemModel(QAbstractItemModel):
    def __init__(self, parent=None, root=None):
        super(EItemModel, self).__init__(parent)
        self.parentWidget = parent
        if root:
            self.rootItem = EBaseItem(root)
        else:
            self.rootItem = EFeatureItem("")

    def removeNonCustom(self):
        children = self.rootItem.childItems.copy()
        for child in children:
            if child.source != "Custom":
                self.removeRow(child.row(),QModelIndex())

    def removeSource(self, source):
        children = self.rootItem.childItems.copy()
        for child in children:
            if child.source == source:
                self.removeRow(child.row(),QModelIndex())

    def toLine(self):
        items = []
        for item in self.rootItem.childItems:
            if len(item.itemData) > 0:
                items.append(";".join(item.itemData).replace(",","$").replace(":","~")+";"+item.source)
        return ",".join(items)

    def toLine_f(self):
        items = []
        for item in self.rootItem.childItems:
            if item.source == "Custom" and len(item.itemData) > 0:
                temp = ";".join(item.itemData).replace(",","$").replace(":","~")+":"
                temp += item.description.replace(",","$").replace(";","`").replace(":","~")
                temp += ";"+item.source
                items.append(temp)
        return ",".join(items)

    def customToLine(self):
        items = []
        for item in self.rootItem.childItems:
            if item.custom:
                items.append(";".join(item.itemData).replace(",","$"))
        return ",".join(items)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        item = index.internalPointer()

        return item.flags()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def appendRow(self, item):
        self.rootItem.appendChild(item)
        item.parentItem = self.rootItem

    def setData(self, index, data, role=Qt.DisplayRole):
        item = index.internalPointer()
        item.setText(data, item.itemData.index(index.data(0)))
        return True

    def removeRow(self, row, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        self.beginRemoveRows(parent, row, row)
        boole = parentItem.removeChild(row)
        self.endRemoveRows()
        return boole

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.rootItem

class EBaseItem():
    itemData = []
    def __init__(self, data, parent=None, edit=False, source="Class"):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []
        self.source = source
        self.flagItem = Qt.ItemFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
        if edit:
            self.setEditable(True)

    def copy(self):
        temp = EBaseItem(self.itemData, self.parentItem, source=self.source)
        for child in self.childItems:
            temp.childItems.append(child.copy())
        temp.flagItem = self.flagItem
        return temp

    def appendChild(self, item):
        self.childItems.append(item)
        item.parentItem = self

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def setEditable(self, bool):
        if bool:
            self.setFlags(self.flags()|Qt.ItemIsEditable)
        else:
            self.setFlags(self.flags()&(~Qt.ItemIsEditable))

    def flags(self):
        return self.flagItem

    def setFlags(self, flags):
        self.flagItem = Qt.ItemFlags(flags)

    def setText(self, text, col=0):
        self.itemData[col] = text

    def text(self, col=0):
        return self.itemData[col]

    def removeChild(self, position):
        if position < 0 or position > len(self.childItems):
            return False

        child = self.childItems.pop(position)
        child.parentItem = None
        del child

        return True

class EFeatureItem(EBaseItem):
    def __init__(self, data, description=None, parent=None, source="Class"):
        super().__init__([data], parent)
        self.source = source
        if not description == None:
            self.appendChild(EFeatureItem(description,parent=self))
        self.description = description

class ETreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.setIndentation(0)
        self.setWordWrap(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = QHeaderView(Qt.Horizontal, self)
        font = header.font()
        font.setPointSize(qApp.font().pointSize() - math.ceil(qApp.font().pointSize()/8))
        header.setFont(font)
        header.setDefaultAlignment(Qt.AlignLeft)
        self.setItemDelegate(WrapEditDelegate(self))
        self.setHeader(header)
        self.setEditTriggers(self.editTriggers()|QAbstractItemView.DoubleClicked)

class EFeatureView(QTreeView):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setIndentation(0)
        self.setWordWrap(True)
        self.setVerticalScrollMode(QTreeView.ScrollPerPixel)
        self.setItemDelegate(ItemWordWrap(self))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if len(self.selectedIndexes()) > 0:
            self.setExpanded(self.selectedIndexes()[0],not (self.isExpanded(self.selectedIndexes()[0])))

    def columnWidth(self, num):
        size = super().columnWidth(num)
        return size

    def resizeEvent(self, e):
        super().resizeEvent(e)

        if self.model():
            self.model().layoutChanged.emit()

        self.viewport().update()

class EAttackView(ETreeView):
    def __init__(self):
        super().__init__()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.setColumnWidth(0,(event.size().width()+1)*0.33)
        self.setColumnWidth(1,(event.size().width()+1)*0.18)
        self.setColumnWidth(2,(event.size().width()+1)*0.19)
        self.setColumnWidth(3,(event.size().width()+1)*0.30)
        self.reset()

class EProfView(ETreeView):
    def __init__(self):
        super().__init__()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.setColumnWidth(0,(event.size().width())*0.27)
        self.setColumnWidth(1,(event.size().width())*0.73)
        self.reset()

class EEquipmentView(ETreeView):
    def __init__(self):
        super().__init__()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.setColumnWidth(0,(event.size().width())*0.80)
        self.setColumnWidth(1,(event.size().width())*0.20)
        self.reset()

    def sizeHint(self):
        size = super().sizeHint()
        if self.minimumWidth() > 0:
            size.setWidth(self.minimumWidth())
        return size

class EditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        return ETextEdit(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data(0))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())
        #index.internalPointer().edited = True
        self.parent.reset()

    def updateEditorGeometry(self, editor, option, index):
        super().updateEditorGeometry(editor, option, index)
        editor.setAlignment(Qt.AlignTop)

class WrapEditDelegate(EditDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        option.displayAlignment = Qt.AlignTop | Qt.AlignLeft

        painter.save()
        font = painter.font()
        font.setPointSize(self.parent.font().pointSize())
        painter.setFont(font)

        super().paint(painter, option, index)
        painter.restore()

    def sizeHint(self, option, index):
        self.initStyleOption(option, index)
        document = QtGui.QTextDocument()
        document.setDocumentMargin(2)
        font = document.defaultFont()
        font.setPointSize(self.parent.font().pointSize())
        document.setDefaultFont(font)
        document.setPlainText(index.data(0))

        width = self.parent.columnWidth(index.column())
        document.setTextWidth(width)

        height = document.size().height()
        return QSize(document.idealWidth(), height)

    def eventFilter(self, editor, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor)
                return True
        return super().eventFilter(editor, event)

class ETextDocument(QTextDocument):
    def setMarkdown(self, text):
        super().setMarkdown(text)
        cursor = QTextCursor(self.firstBlock())
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()

class SpellDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.parent = parent

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonPress and type(index.data(0)) == bool:
            model.setData(index, (not index.data(0)), Qt.UserRole + 1)
            self.parent.model().layoutChanged.emit()
            return True
        elif event.type() == QEvent.MouseButtonPress:
            cIndex = self.parent.model().createIndex(index.row(), 0, index.internalPointer())
            self.parent.setExpanded(cIndex, not (self.parent.isExpanded(cIndex)))
            self.parent.model().layoutChanged.emit()
            return False
        elif event.type() == QEvent.MouseButtonDblClick:
            index.internalPointer().source.dialog.show()
        self.parent.model().layoutChanged.emit()
        return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        option.displayAlignment = Qt.AlignTop | Qt.AlignLeft
        painter.save()

        qApp.style().drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter)
        if type(index.data(0)) != bool:
            text = index.data(0)
            document = ETextDocument()
            document.setDocumentMargin(2)
            font = document.defaultFont()
            font.setPointSize(self.parent.font().pointSize())
            document.setDefaultFont(font)

            if option.widget.model().parentWidget.rootIndex() == index.parent():
                document.setHtml(text)
                document.setTextWidth(option.rect.width())
                painter.translate(option.rect.x(), option.rect.y())
                document.drawContents(painter)

            else:
                if index.column() == 0:
                    document.setMarkdown(text.replace("<br>","\n\n"))
                    width = 0
                    for num in range(0, self.parent.columnCount()):
                        width += self.parent.columnWidth(num)
                    document.setTextWidth(width)
                    painter.translate(option.rect.x(), option.rect.y())
                    document.drawContents(painter)

        else:
            cbOpt = QStyleOptionButton()
            cbOpt.rect = self.getCBRect(option)
            cbOpt.displayAlignment = Qt.AlignCenter
            cbOpt.state = (QStyle.State_On if index.data(0) else QStyle.State_Off)|QStyle.State_Enabled

            qApp.style().drawControl(QStyle.CE_CheckBox, cbOpt, painter)

        painter.restore()

    def sizeHint(self, option, index, startCol = 1):
        self.initStyleOption(option, index)
        document = ETextDocument()

        document.setDocumentMargin(2)
        font = document.defaultFont()
        font.setPointSize(self.parent.font().pointSize())
        document.setDefaultFont(font)

        if type(index.data(0)) == bool:
            text = ""
        else:
            text = index.data(0)

        if option.widget.model().parentWidget.rootIndex() == index.parent():
            document.setHtml(text)

            width = self.parent.columnWidth(index.column())
            document.setTextWidth(width-2)
            height = document.size().height()
            return QSize(document.idealWidth(), height)
        else:
            if index.column() == 0:
                document.setMarkdown(text.replace("<br>","\n\n"))
            else:
                document.setMarkdown(index.internalPointer().itemData[0].replace("<br>","\n\n"))

            width = 0
            for num in range(startCol, self.parent.columnCount()):
                width += self.parent.columnWidth(num)
            document.setTextWidth(width)

            height = document.size().height()
            return QSize(document.idealWidth(), height)

    def getCBRect(self, option):
        opt_button = QStyleOptionButton()
        opt_button.operator = option
        sz = qApp.style().subElementRect(QStyle.SE_ViewItemCheckIndicator, opt_button)
        r = option.rect
        # center 'sz' within 'r'
        dx = (r.width() - sz.width())/2
        dy = (r.height() - sz.height())/2
        r.setTopLeft(r.topLeft() + QPoint(int(dx),int(dy)))
        r.setWidth(sz.width())
        r.setHeight(sz.height())

        return r

class InvocDelegate(SpellDelegate):
    def sizeHint(self, option, index, startCol=0):
        return super().sizeHint(option, index, startCol)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonPress:
            if self.parent.clickExpand:
                cIndex = self.parent.model().createIndex(index.row(), 0, index.internalPointer())
                self.parent.setExpanded(cIndex, not (self.parent.isExpanded(cIndex)))
                self.parent.model().layoutChanged.emit()
                return False
            else:
                return False
        elif event.type() == QEvent.MouseButtonDblClick:
            if self.parent.cardShow:
                index.internalPointer().source.dialog.show()
                return True
            else:
                return True
        return super().editorEvent(event, model, option, index)

class ItemWordWrap(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.parent = parent

    def paint(self, painter, option, index):
        text = index.data(0).replace("\n","<br>")
        if option.widget.model().parentWidget.rootIndex() == index.parent():
            text = "<b>"+text+"</b><hr>"
            fontSize = self.parent.font().pointSize()
        else:
            fontSize = self.parent.font().pointSize() - math.floor(self.parent.font().pointSize()/8)

        document = QTextDocument()
        document.setDocumentMargin(2)
        font = document.defaultFont()
        font.setPointSize(fontSize)
        document.setDefaultFont(font)

        document.setHtml(text)
        document.setTextWidth(option.rect.width())
        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        self.initStyleOption(option, index)
        text = index.data(0).replace("\n","<br>")

        document = QTextDocument()
        document.setDocumentMargin(2)

        if option.widget.model().parentWidget.rootIndex() == index.parent():
            text = "<b>"+text+"</b><hr>"
            fontSize = self.parent.font().pointSize()
        else:
            fontSize = self.parent.font().pointSize() - math.floor(self.parent.font().pointSize()/8)

        font = document.defaultFont()
        font.setPointSize(fontSize)
        document.setDefaultFont(font)

        document.setHtml(text)

        width = self.parent.columnWidth(index.column())
        document.setTextWidth(width)

        height = document.size().height()

        return QSize(width, height)

class ETextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        doc = self.document()
        doc.setDocumentMargin(2)
        self.setDocument(doc)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            super().focusOutEvent(QFocusEvent(QEvent.FocusOut))
        else:
            super().keyPressEvent(event)

class ELabeledEdit(QGroupBox):
    groupBoxStyleSheet = """
    QGroupBox {
        border: 1px solid gray;
        background: white;
        padding: 0px 0px 8px 0px;
        margin: 0px 0px 4px 0px;
    }
    QGroupBox::title {
        subcontrol-position: bottom center;
        bottom: -4px;
    }
    """
    leftGroupBoxStyleSheet = """
    QGroupBox {
        border: 1px solid gray;
        background: white;
        padding: 0px 0px 0px 8px;
        margin: 0px 0px 0px 4px;
    }
    QGroupBox::title {
        subcontrol-position: left center;
        left: -4px;
    }
    """
    editStyleSheet = """
    QTextEdit {
        border: 0px;
    }
    """
    def __init__(self, title="", height=90, width=None, scrollbars=True, enter=True):
        super().__init__(title)
        if enter:
            self.edit = QTextEdit()
        else:
            self.edit = ETextEdit()

        if not scrollbars:
            self.edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.setStyleSheet(self.groupBoxStyleSheet)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)
        self.edit.setStyleSheet(self.editStyleSheet)
        self.layout.addWidget(self.edit)

    def setAlignment(self, alignment):
        self.edit.setAlignment(alignment)

    def setPointSize(self, size):
        font = self.edit.document().defaultFont()
        font.setPointSize(size)
        doc = self.edit.document()
        doc.setDefaultFont(font)
        self.edit.setDocument(doc)

    def setLeftAligned(self):
        self.setStyleSheet(self.leftGroupBoxStyleSheet)

class ELabel(QLabel):
    def __init__(self, text="", fontSize=None, bold=False, width=None, height=None,add=True,alignment=None):
        super().__init__(text)
        font = self.font()
        if fontSize:
            font.setPointSize(fontSize)
        font.setBold(bold)
        self.setFont(font)
        if alignment:
            self.setAlignment(alignment)
        if add:
            self.setFrameShape(QFrame.StyledPanel)
            self.setAlignment(Qt.AlignCenter)
            self.setBackgroundRole(QPalette.Base)
            self.setAutoFillBackground(True)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

class ELineEdit(QLineEdit):
    def __init__(self, text="", fontSize=14, bold=False, width=None, height=None, background=None, frame=None):
        super().__init__(text)
        font = self.font()
        font.setPointSize(fontSize)
        font.setBold(bold)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(font)
        self.setValidator(QIntValidator())
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        if background:
            p = self.palette()
            p.setColor(self.backgroundRole(),p.color(background))
            self.setPalette(p)
        if frame:
            option = QStyleOptionFrame()
            option.frameShape = QFrame.StyledPanel
            option.lineWidth = 0
            option.midLineWidth = 0
            option.features = QStyleOptionFrame.Flat
            self.initStyleOption(option)

class ECheckBox(QCheckBox):
    def __init__(self, enabled=True, size=None):
        super().__init__()
        if not enabled:
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.setFocusPolicy(Qt.NoFocus)
        if size:
            self.setStyleSheet("QCheckBox::indicator { width:"+str(size)+"px; height: "+str(size)+"px; }");

    def setCheckState(self,state):
        if type(state) == type(True):
            if state:
                super().setCheckState(Qt.Checked)
            else:
                super().setCheckState(Qt.Unchecked)
        else:
            super().setCheckState(state)
