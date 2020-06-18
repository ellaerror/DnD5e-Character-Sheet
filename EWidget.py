from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random, math, copy
from EFeature import *

class EClassFeature():
    def __init__(self, name, description):
        self.name = name
        self.description = description

def importClassFeatures(file_Path):
    input = open(file_Path, "rb")
    feats = []
    data = input.readline()
    data = input.readline()
    while data:
        data = data.strip().split(b"\t")
        feats.append(EClassFeature(str(data[0],"utf8"), str(data[1],"utf8")))
        data = input.readline()
    return feats

class EInvocation():
    def __init__(self, line_Data):
        if type(line_Data) == bytes:
            line_Data = str(line_Data.strip(b"\n"),"utf8")
        else:
            line_Data = line_Data.strip("\n")
        data = line_Data.split("\t")
        self.name = data[0]
        self.level_Req = int(data[1])
        self.other_Req = data[2]
        self.description = data[3].replace("<br>","\n\n")
        self.source = data[4]

        self.fullDescription = "## "+self.name+"\n\n"
        if self.level_Req > 0 or len(self.other_Req) > 0:
            self.fullDescription += "**Requirements:** "
            if self.level_Req > 0:
                self.fullDescription += str(self.level_Req)+" level"
                if len(self.other_Req) > 0:
                    self.fullDescription += ", "
            if len(self.other_Req) > 0:
                self.fullDescription += self.other_Req
            self.fullDescription += "\n\n"
        self.fullDescription += "**Source:** "+self.source+"\n\n"
        self.fullDescription += self.description
        self.dialog = SpellCardDialog(self)

def importInvocations(file_Path):
    input = open(file_Path, "rb")
    invocations = []
    data = input.readline()
    data = input.readline()
    while data:
        invocations.append(EInvocation(data))
        data = input.readline()
    return invocations

class ESpell():
    def __init__(self, line_Data):
        if type(line_Data) == bytes:
            line_Data = str(line_Data.strip(b"\n"),"utf8")
        else:
            line_Data = line_Data.strip("\n")
        data = line_Data.split("\t")
        self.line_Data = line_Data
        self.level = int(data[0])
        self.name = data[1]
        self.school = data[2]
        self.castingTime = data[3]
        self.range = data[4]
        self.components = data[5]
        self.materials = data[6]
        self.duration = data[7]
        self.concentration = data[8]
        self.ritual = data[9]
        self.classes = data[10].split(",")
        self.source = data[11]
        self.details = data[12]
        self.atkThrow = data[13]
        self.crTag = ""
        if self.ritual == "TRUE":
            self.crTag += "R"
        if self.concentration == "TRUE":
            self.crTag += "C"

        self.description = ""

        if len(self.atkThrow) > 1:
            self.description += "**Attack/Saving Throw:** "+self.atkThrow+"<br>"

        self.description += "**Range:** "+self.range+"<br>"
        self.description += "**Duration:** "+self.duration+"<br>"

        if len(self.materials) > 1:
            self.description += "**Material Components:** "+self.materials+"<br>"

        if len(self.castingTime.split(",")) > 1:
            c = self.castingTime.split(",")[0].strip()
        else:
            c = self.castingTime

        self.fullDescription = "## "+self.name+"<br>"
        if self.level > 0:
            self.fullDescription += "*level "+str(self.level)+" "+self.school
        else:
            self.fullDescription += "*"+self.school+" cantrip"
        if len(self.crTag) > 0:
            self.fullDescription += " ("+self.crTag+")"
        self.fullDescription += "* <br>**Casting Time:** "+self.castingTime+"<br>"
        self.fullDescription += "**Components:** "+self.components+"<br>"
        self.fullDescription += self.description+"<br>"
        self.fullDescription += self.details

        self.data = [self.name,self.crTag,c,self.components]

        self.dialog = SpellCardDialog(self)

    def importSpells(file_Path):
        finalList = []
        input = open(file_Path, "rb")
        data = input.readline()
        data = input.readline()
        while data:
            finalList.append(ESpell(data))
            data = input.readline()
        return finalList

    def toLine(self):
        return "\t".join(self.line_Data)+"\n"

    def toLine_C(self):
        return self.name+","+str(self.level)+"\n"

class ESpellModel(QAbstractItemModel):
    def __init__(self, parent=None, root=None):
        super(ESpellModel, self).__init__(parent)
        self.parentWidget = parent
        if root:
            self.rootItem = EBaseItem(root)
        else:
            self.rootItem = EBaseItem([""])

    def createModelFromClass(self, parent, className, subclassName, race):
        newModel = ESpellModel(parent=parent, root=self.rootItem.itemData.copy())
        for child in self.rootItem.childItems:
            if className.lower() in child.source.classes or subclassName.lower() in child.source.classes or race.lower() in child.source.classes:
                newModel.appendRow(child.copy())
        return newModel

    def createModelFromLevel(self, parent, level):
        newModel = ESpellModel(parent=parent, root=self.rootItem.itemData.copy())
        for child in self.rootItem.childItems:
            if level >= child.source.level_Req:
                temp = child.copy()
                for num in range(0, len(temp.itemData)):
                    temp.itemData[num] = "<b>"+temp.itemData[num]+"</b>"
                newModel.appendRow(temp)
        return newModel

    def sort(self, int):
        self.rootItem.childItems.sort(key=lambda x: x.itemData[1] )

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
        if parentItem == None:
            #print("ORPHAN DATA:",childItem.itemData)
            return QModelIndex()

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

class ESpellListWidget(QTreeView):
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
        header.setMinimumSectionSize(5)
        self.setItemDelegate(SpellDelegate(self))
        self.setHeader(header)
        #self.setEditTriggers(self.editTriggers()|QAbstractItemView.DoubleClicked)

    def columnCount(self):
        return self.model().columnCount(QModelIndex())

    def setExpanded(self, index, bool):
        super().setExpanded(index, bool)
        if self.model():
            self.model().layoutChanged.emit()
        self.viewport().update()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        # PREPARED
        self.setColumnWidth(0,17)
        # NAME
        self.setColumnWidth(1,(event.size().width()-15)*0.52)
        # CR
        self.setColumnWidth(2,(event.size().width()-15)*0.11)
        # TIME
        self.setColumnWidth(3,(event.size().width()-15)*0.25)
        # COMPONENTS
        self.setColumnWidth(4,(event.size().width()-15)*0.12)

        # THIS IS ABSOLUTELY VITAL
        # I CANNOT UNDERSTATE THIS
        if self.model():
            self.model().layoutChanged.emit()

        self.viewport().update()


class AddSpellDialog(QDialog):
    def __init__(self, parent=None, windowTitle="Add new spells"):
        super().__init__(parent)
        self.spells = None
        self.setWindowTitle(windowTitle)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.mainLayout = QGridLayout()
        self.mainLayout.setContentsMargins(4,4,4,4)
        self.mainLayout.setSpacing(2)
        self.setLayout(self.mainLayout)

        self.initUI()

        self.exit_Button = QPushButton("Cancel")
        self.exit_Button.clicked.connect(self.close)

        self.addSpell_Button = QPushButton("Add")
        self.addSpell_Button.clicked.connect(self.addSpell)

        self.mainLayout.addWidget(self.spells_View,0,0,1,2)
        self.mainLayout.addWidget(self.exit_Button,1,0)
        self.mainLayout.addWidget(self.addSpell_Button,1,1)

    def initUI(self):
        self.spells_View = ESpellListWidget()
        self.spells_List = ESpellModel(parent=None, root=["","Name","C/R","Time","VSM"])

    def addSpell(self):
        self.spells = []
        toRemove = []
        for child in self.spells_List.rootItem.childItems:
            if child.itemData[0]:
                self.spells.append(child.copy())
                toRemove.append(child)
        for child in toRemove:
            self.spells_List.removeRow(child.row())
        self.close()

    def prepExec(self, className="None", subclassName="None", race="None"):
        self.spells=None
        subclassName = className+" ("+subclassName+")"
        self.displaySpell_List = self.spells_List.createModelFromClass(self.spells_View, className, subclassName, race)
        self.spells_View.setModel(self.displaySpell_List)
        self.spells_View.setExpanded(self.spells_View.rootIndex(), True)
        self.resize(400,500)
        super().exec_()

class ESpellItem(EBaseItem):
    def __init__(self, data, parent=None, source=ESpell):
        super().__init__(data, parent)
        self.source = source

    def copy(self):
        temp = ESpellItem(self.itemData, self.parentItem, source=self.source)
        for child in self.childItems:
            temp.childItems.append(child.copy())
        temp.flagItem = self.flagItem
        return temp

class SpellCardDialog(QDialog):
    def __init__(self, spell, parent=None):
        super().__init__(parent)
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle(spell.name+" Card")

        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.card_Text = QTextEdit()
        self.card_Text.setReadOnly(True)
        try:
            self.card_Text.setMarkdown(spell.fullDescription.replace("<br>","\n\n"))
        except Exception as e:
            print(e, type(self.card_Text))
            self.card_Text.setPlainText(spell.fullDescription.replace("<br>","\n"))

        self.mainLayout.addWidget(self.card_Text,0,0)

    def setParent(self, parent):
        self.parent = parent

    def show(self):
        self.resize(350,400)
        super().show()

class SpellSlotWidget(QGroupBox):
    groupBoxStyleSheet_NoTitle = """
    QGroupBox {
        border: 1px solid gray;
        padding: 0px 0px 0px 0px;
        margin: 0px 0px 0px 0px;
    }
    """
    def __init__(self, level, spellList, parent=None):
        super().__init__()
        self.setSizes()
        self.parent = parent
        self.level = level
        self.addSpellDialog = AddSpellDialog(self)

        self.mainLayout = QGridLayout()
        self.mainLayout.setContentsMargins(4,4,4,4)
        self.mainLayout.setSpacing(2)

        self.setLayout(self.mainLayout)
        self.setStyleSheet(self.groupBoxStyleSheet_NoTitle)

        self.initUI(spellList, level)

        self.delSpell_Button = QPushButton("-")
        self.delSpell_Button.setFixedHeight(20)
        self.delSpell_Button.clicked.connect(self.delSpell)

        self.addSpell_Button = QPushButton("+")
        self.addSpell_Button.setFixedHeight(20)
        self.addSpell_Button.clicked.connect(self.addSpell)

        button_Layout = QHBoxLayout()
        button_Layout.setContentsMargins(0,0,0,0)
        button_Layout.addWidget(self.delSpell_Button)
        button_Layout.addWidget(self.addSpell_Button)

        self.mainLayout.addWidget(self.spells_View,2,0,1,3)
        self.mainLayout.addLayout(button_Layout,3,0,1,3)

    def initUI(self, spellList, level):
        self.spells_View = ESpellListWidget()
        font = self.spells_View.font()
        font.setPointSize(self.default_FS)
        self.spells_View.setFont(font)
        self.spells_List = ESpellModel(parent=self.spells_View, root=["","Name","C/R","Time","VSM"])
        self.spells_View.setModel(self.spells_List)

        if self.level != 0:
            self.slots    = ELabel("0", fontSize=self.big_FS, bold=False, width=self.big_FS*6)
            self.expended = ELineEdit("0", fontSize=self.big_FS, bold=False, height=(self.big_FS*2)-3)

            self.mainLayout.addWidget(ELabel("Level",add=False,fontSize=self.small_FS),0,0,Qt.AlignHCenter|Qt.AlignTop)
            self.mainLayout.addWidget(ELabel("Total Slots",add=False,fontSize=self.small_FS),0,1,Qt.AlignHCenter|Qt.AlignTop)
            self.mainLayout.addWidget(ELabel("Expended Slots",add=False,fontSize=self.small_FS),0,2,Qt.AlignHCenter|Qt.AlignTop)

            self.mainLayout.addWidget(ELabel(str(level), fontSize=self.big_FS, bold=False, width=self.big_FS*3),1,0,Qt.AlignTop)
            self.mainLayout.addWidget(self.slots,    1,1,Qt.AlignTop)
            self.mainLayout.addWidget(self.expended, 1,2,Qt.AlignTop)
        else:
            self.known_Label = ELabel("0",fontSize=self.big_FS, bold=False)

            self.mainLayout.addWidget(ELabel("Cantrips Known",add=False,fontSize=self.small_FS),0,2,Qt.AlignTop|Qt.AlignHCenter)
            self.mainLayout.addWidget(self.known_Label                                 ,1,2,Qt.AlignTop)
            self.mainLayout.addWidget(ELabel("Cantrips", fontSize=self.big_FS, bold=False),     1,0,1,2,Qt.AlignTop)

        for spell in spellList:
            if spell.level == self.level:
                mainSpell = ESpellItem([False]+spell.data, source=spell)
                mainSpell.appendChild(ESpellItem([spell.description], source=spell))
                self.addSpellDialog.spells_List.appendRow(mainSpell)

    def addSpell(self):
        if self.parent.currentCharacter.subclass.basename == "land":
            sc = self.parent.currentCharacter.druidLand
        else:
            sc = self.parent.currentCharacter.subclass.basename
        self.addSpellDialog.prepExec(self.parent.currentCharacter.mainclass.name, sc, self.parent.currentCharacter.subrace.name)
        if self.addSpellDialog.spells:
            for spell in self.addSpellDialog.spells:
                spell.itemData[0] = False
                self.spells_List.appendRow(spell)
                self.parent.currentCharacter.spells.append(spell.source)
            self.spells_View.setExpanded(self.spells_View.rootIndex(), True)

    def delSpell(self):
        try:
            copy = self.spells_View.selectedIndexes()[0].internalPointer().copy()
            copy.itemData[0] = False
            self.parent.currentCharacter.spells.remove(copy.source)
            self.addSpellDialog.spells_List.appendRow(copy)
            self.addSpellDialog.spells_List.sort(1)
            self.spells_List.removeRow(self.spells_View.selectedIndexes()[0].row(), self.spells_View.selectedIndexes()[0].parent())
            self.addSpellDialog.spells_View.setExpanded(self.addSpellDialog.spells_View.rootIndex(), True)
        except Exception as e:
            print(e)

    def clearSpells(self):
        toRemove = []
        for spell in self.spells_List.rootItem.childItems:
            copy = spell.copy()
            copy.itemData[0] = False
            self.addSpellDialog.spells_List.appendRow(copy)
            toRemove.append(spell)
        for spell in toRemove:
            self.spells_List.removeRow(spell.row())
        self.addSpellDialog.spells_View.setExpanded(self.addSpellDialog.spells_View.rootIndex(), True)
        self.addSpellDialog.spells_List.sort(1)

    def setSizes(self):
        font = qApp.font()
        size = font.pointSize()
        self.default_FS = size # 8
        self.small_FS = size - math.ceil(size/8) # 7
        self.middle_FS = size + math.floor(size/5) # 9
        self.medium_FS = size + math.ceil(size/4) # 10
        self.big_FS = size + math.ceil(size/2) # 14
        self.large_FS = size * 2 # 16
        self.huge_FS = math.ceil(size * 2.5)

    def setMaxSlots(self, int):
        if self.level != 0:
            self.slots.setText(str(int))
        else:
            self.known_Label.setText(str(int))

    def updateFromKeys(self, spellKey):
        correctLevel = [x[0] for x in spellKey if int(x[1]) == self.level]
        toRemove = []
        for spell in self.addSpellDialog.spells_List.rootItem.childItems:
            if spell.source.name in correctLevel:
                self.spells_List.appendRow(spell.copy())
                self.parent.currentCharacter.spells.append(spell.source)
                toRemove.append(spell)
        for spell in toRemove:
            self.addSpellDialog.spells_List.removeRow(spell.row())
        self.spells_View.expandAll()
        self.spells_View.collapseAll()
        self.spells_View.setExpanded(self.spells_View.rootIndex(), True)
        self.spells_View.viewport().update()

class EInvocationList(SpellSlotWidget):
    def __init__(self, invocationList, parent=None):
        super().__init__(0, invocationList, parent)

    def initUI(self, invocationList, level):
        self.addSpellDialog = AddInvocDialog(self)

        self.spells_View = EInvocListWidget()
        font = self.spells_View.font()
        font.setPointSize(self.default_FS)
        self.spells_View.setFont(font)
        self.spells_List = ESpellModel(parent=self.spells_View, root=["Name"])
        self.spells_View.setModel(self.spells_List)

        self.known_Label = ELabel("2",fontSize=self.big_FS, bold=False)
        self.mainLayout.addWidget(ELabel("Invocations Known",add=False,fontSize=self.small_FS),0,2,Qt.AlignTop|Qt.AlignHCenter)
        self.mainLayout.addWidget(self.known_Label                                 ,1,2,Qt.AlignTop)
        self.mainLayout.addWidget(ELabel("Invocations", fontSize=self.big_FS, bold=False),     1,0,1,2,Qt.AlignTop)

        for invoc in invocationList:
            mainSpell = ESpellItem([invoc.name, invoc.other_Req], source=invoc)
            mainSpell.appendChild(ESpellItem([invoc.description], source=invoc))
            self.addSpellDialog.spells_List.appendRow(mainSpell)

    def addSpell(self):
        self.addSpellDialog.prepExec(self.parent.currentCharacter.level)
        if self.addSpellDialog.spells:
            for spell in self.addSpellDialog.spells:
                self.spells_List.appendRow(spell)
                self.parent.currentCharacter.spells.append(spell.source)
            self.spells_View.setExpanded(self.spells_View.rootIndex(), True)

    def delSpell(self):
        try:
            copy = self.spells_View.selectedIndexes()[0].internalPointer().copy()
            self.parent.currentCharacter.spells.remove(copy.source)
            self.addSpellDialog.spells_List.appendRow(copy)
            self.addSpellDialog.spells_List.sort(1)
            self.spells_List.removeRow(self.spells_View.selectedIndexes()[0].row(), self.spells_View.selectedIndexes()[0].parent())
            self.addSpellDialog.spells_View.setExpanded(self.addSpellDialog.spells_View.rootIndex(), True)
        except Exception as e:
            print(e)

class EInvocListWidget(ESpellListWidget):
    def __init__(self, clickExpand=True, cardShow=True):
        super().__init__()
        self.setItemDelegate(InvocDelegate(self))
        self.clickExpand = clickExpand
        self.cardShow = cardShow

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # NAME
        if self.columnCount() == 1:
            self.setColumnWidth(0, event.size().width())
        else:
            self.setColumnWidth(0, event.size().width()/2)
            self.setColumnWidth(1, event.size().width()/2)

        # THIS IS ABSOLUTELY VITAL
        # I CANNOT UNDERSTATE THIS
        if self.model():
            self.model().layoutChanged.emit()

        self.viewport().update()

class AddInvocDialog(AddSpellDialog):
    def __init__(self, parent=None, windowTitle="Add an Invocation"):
        super().__init__(parent, windowTitle)

    def initUI(self):
        self.spells_View = EInvocListWidget(clickExpand=False, cardShow=False)
        self.spells_List = ESpellModel(parent=None, root=["Name", "Prerequisite"])

    def prepExec(self, level):
        self.spells=None
        self.displaySpell_List = self.spells_List.createModelFromLevel(self.spells_View, level)
        self.spells_View.setModel(self.displaySpell_List)
        self.spells_View.expandAll()
        self.resize(400,500)
        super().exec_()

    def addSpell(self):
        invocation = self.spells_View.selectedIndexes()[0].internalPointer()
        if invocation.parent().itemData != self.spells_List.rootItem.itemData:
            self.spells = [invocation.parent()]
        else:
            self.spells = [invocation]
        self.spells_List.removeRow(invocation.row())
        self.close()

class ESpellWidget(QWidget):
    groupBoxStyleSheet_NoTitle = """
    QGroupBox {
        border: 1px solid gray;
        padding: 0px 0px 0px 0px;
        margin: 0px 0px 0px 0px;
    }
    """
    groupBoxStyleSheet = """
    QGroupBox {
        border: 1px solid gray;
        padding: 0px 0px 4px 0px;
        margin: 0px 0px 4px 0px;
    }
    QGroupBox::title {
        subcontrol-position: bottom center;
        bottom: -3px;
    }
    """
    scoreNames = ["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"]
    def __init__(self, parent=None, character=None):
        super().__init__(parent)
        self.allSpells = ESpell.importSpells("Vars\\finalSpells.tsv")
        self.invocations = importInvocations("Vars\\invocations.tsv")
        self.parent = parent
        self.setSizes()
        self.initUI()
        self.updateCharacter(character)

    def createSpellLists(self, spellKey):
        for widget in self.spellSlotWidgets:
            widget.updateFromKeys(spellKey)

    def updateCharacter(self, character):
        self.currentCharacter = character

        if not self.currentCharacter.mainclass.spellcasting:
            if self.currentCharacter.subclass.spellcasting:
                modIndex = self.scoreNames.index(self.currentCharacter.subclass.spellcastingAbility)
                if self.currentCharacter.subclass.name != self.casterClass_Label.text():
                    for widget in self.spellSlotWidgets:
                        widget.clearSpells()
                    self.casterClass_Label.setText(self.currentCharacter.subclass.name)
                self.spellcastingAbility_Label.setText(self.currentCharacter.subclass.spellcastingAbility)
                self.spellSaveDC_Label.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.pb+8)[1:])
                self.spellAttackBonus_Label.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.pb))
                spellsKnown = self.currentCharacter.subclass.spellsKnown[self.currentCharacter.level-1]
                if spellsKnown == "-1":
                    self.spellsKnown_Label.setText("N/A")
                else:
                    self.spellsKnown_Label.setText(str(spellsKnown))
                self.preparableSpells.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.level)[1:])
                slevel = 0
                for widget in self.spellSlotWidgets:
                    widget.setMaxSlots(self.currentCharacter.subclass.spellSlots[self.currentCharacter.level-1][slevel])
                    slevel+=1
            else:
                self.casterClass_Label.setText("None")
                self.spellcastingAbility_Label.setText("")
                self.spellSaveDC_Label.setText("0")
                self.spellAttackBonus_Label.setText("+0")
                self.spellsKnown_Label.setText("0")
                self.preparableSpells.setText("0")
        else:
            modIndex = self.scoreNames.index(self.currentCharacter.mainclass.spellcastingAbility)
            if self.currentCharacter.mainclass.name != self.casterClass_Label.text():
                for widget in self.spellSlotWidgets:
                    widget.clearSpells()
                self.casterClass_Label.setText(self.currentCharacter.mainclass.name)
            self.spellcastingAbility_Label.setText(self.currentCharacter.mainclass.spellcastingAbility)
            self.spellSaveDC_Label.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.pb+8)[1:])
            self.spellAttackBonus_Label.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.pb))
            spellsKnown = self.currentCharacter.mainclass.spellsKnown[self.currentCharacter.level-1]
            if spellsKnown == "-1":
                self.spellsKnown_Label.setText("N/A")
            else:
                self.spellsKnown_Label.setText(str(spellsKnown))
            self.preparableSpells.setText(self.currentCharacter.getModString(modIndex, add=self.currentCharacter.level)[1:])
            slevel = 0
            for widget in self.spellSlotWidgets:
                widget.setMaxSlots(self.currentCharacter.mainclass.spellSlots[self.currentCharacter.level-1][slevel])
                slevel+=1

        if self.currentCharacter.mainclass.name == "Sorcerer" and self.currentCharacter.level > 1:
            self.sp_Box.show()
            self.sp_Edit.setText(str(self.currentCharacter.level))
            self.maxSP_Label.setText(str(self.currentCharacter.level))
        else:
            self.sp_Box.hide()

        if self.currentCharacter.mainclass.name == "Warlock" and self.currentCharacter.level > 1:
            self.invocations_Box.show()
            level = self.currentCharacter.level
            if level < 5:
                self.invocations_Box.known_Label.setText("2")
            elif level == 5 or level == 6:
                self.invocations_Box.known_Label.setText("3")
            elif level == 7 or level == 8:
                self.invocations_Box.known_Label.setText("4")
            elif level >= 9 and level <= 11:
                self.invocations_Box.known_Label.setText("5")
            elif level >= 12 and level <= 14:
                self.invocations_Box.known_Label.setText("6")
            elif level >= 15 and level <= 17:
                self.invocations_Box.known_Label.setText("7")
            else:
                self.invocations_Box.known_Label.setText("8")
        else:
            self.invocations_Box.hide()

    def initUI(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        #
        # HEADER
        #
        header_Layout = QGridLayout()
        header_Layout.setContentsMargins(4,4,4,4)
        header_Layout.setSpacing(2)

        large_w = self.large_FS*6
        large_h = self.large_FS*2

        medium_w = self.large_FS*6
        medium_h = self.large_FS*2

        self.casterClass_Label =         ELabel("Wizard",fontSize=self.large_FS, bold=False, height=large_h)
        self.spellcastingAbility_Label = ELabel("Intelligence",fontSize=self.large_FS, bold=False, height=large_h)
        self.spellSaveDC_Label =         ELabel("0",fontSize=self.large_FS, bold=False, height=large_h, width=large_w)
        self.spellAttackBonus_Label =    ELabel("+0",fontSize=self.large_FS, bold=False, height=large_h, width=large_w)
        self.spellsKnown_Label =         ELabel("N/A",fontSize=self.large_FS, bold=False, height=large_h, width=large_w)
        self.preparableSpells =          ELabel("0",fontSize=self.large_FS, bold=False, height=large_h, width=large_w)

        header_Layout.addWidget(self.casterClass_Label,        0,0)
        header_Layout.addWidget(QLabel("Casting Class"),       1,0,Qt.AlignCenter)
        header_Layout.addWidget(self.spellcastingAbility_Label,0,1)
        header_Layout.addWidget(QLabel("Spellcasting Ability"),1,1,Qt.AlignCenter)
        header_Layout.addWidget(self.spellSaveDC_Label,        0,2)
        header_Layout.addWidget(QLabel("Spell Save DC"),       1,2,Qt.AlignCenter)
        header_Layout.addWidget(self.spellAttackBonus_Label,   0,3)
        header_Layout.addWidget(QLabel("Spell Attack Bonus"),  1,3,Qt.AlignCenter)
        header_Layout.addWidget(self.spellsKnown_Label,        0,4)
        header_Layout.addWidget(QLabel("Spells Known"),        1,4,Qt.AlignCenter)
        header_Layout.addWidget(self.preparableSpells,         0,5)
        header_Layout.addWidget(QLabel("Preparable Spells"),   1,5,Qt.AlignCenter)

        #
        # SPELL SLOTS
        #
        self.cantrip_Box  = SpellSlotWidget(0, self.allSpells, parent=self)
        self.level1_Slots = SpellSlotWidget(1, self.allSpells, parent=self)
        self.level2_Slots = SpellSlotWidget(2, self.allSpells, parent=self)
        self.level3_Slots = SpellSlotWidget(3, self.allSpells, parent=self)
        self.level4_Slots = SpellSlotWidget(4, self.allSpells, parent=self)
        self.level5_Slots = SpellSlotWidget(5, self.allSpells, parent=self)
        self.level6_Slots = SpellSlotWidget(6, self.allSpells, parent=self)
        self.level7_Slots = SpellSlotWidget(7, self.allSpells, parent=self)
        self.level8_Slots = SpellSlotWidget(8, self.allSpells, parent=self)
        self.level9_Slots = SpellSlotWidget(9, self.allSpells, parent=self)
        self.spellSlotWidgets = [
            self.cantrip_Box,
            self.level1_Slots,
            self.level2_Slots,
            self.level3_Slots,
            self.level4_Slots,
            self.level5_Slots,
            self.level6_Slots,
            self.level7_Slots,
            self.level8_Slots,
            self.level9_Slots
        ]
        #
        # ALT SPELLCASTING THINGS:
        #

        # Sorcery points
        sp_Layout = QGridLayout()
        sp_Layout.setContentsMargins(4,4,4,4)
        sp_Layout.setSpacing(2)
        self.sp_Box = QGroupBox()
        self.sp_Box.setStyleSheet(self.groupBoxStyleSheet_NoTitle)
        self.sp_Box.setLayout(sp_Layout)

        self.sp_Edit = ELineEdit("0",fontSize=self.medium_FS)
        self.sp_Edit.setFixedWidth(self.sp_Edit.sizeHint().height())
        self.sp_Edit.setValidator(QIntValidator())
        self.maxSP_Label = ELabel("0",fontSize=self.medium_FS,
            width=self.sp_Edit.sizeHint().height(),
            height=self.sp_Edit.sizeHint().height()
        )

        sp_Layout.addWidget(self.sp_Edit,    0,0, Qt.AlignCenter)
        sp_Layout.addWidget(ELine(vertical=True),         0,1)
        sp_Layout.addWidget(self.maxSP_Label,0,2, Qt.AlignCenter)
        sp_Layout.addWidget(QLabel("Sorcery Points"),1,0,1,3)

        header_Layout.addWidget(self.sp_Box, 0,6,2,1)
        self.sp_Box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.sp_Box.hide()

        # Invocations
        self.invocations_Box = EInvocationList(self.invocations, self)

        # Arcanums

        # Wild shape (?)

        # Channel Divinity (?)

        #
        # ADD THINGS TO LAYOUT
        #
        col1Layout = QVBoxLayout()
        col1Layout.setSpacing(2)
        col2Layout = QVBoxLayout()
        col2Layout.setSpacing(2)
        col3Layout = QVBoxLayout()
        col3Layout.setSpacing(2)

        self.layout.addLayout(col1Layout,2,0)
        self.layout.addLayout(col2Layout,2,1)
        self.layout.addLayout(col3Layout,2,2)

        self.layout.setRowStretch(2,1)

        col1Layout.addWidget(self.cantrip_Box)
        col1Layout.addWidget(self.level1_Slots)
        col1Layout.addWidget(self.level2_Slots)

        col2Layout.addWidget(self.level3_Slots)
        col2Layout.addWidget(self.level4_Slots)
        col2Layout.addWidget(self.level5_Slots)
        col2Layout.addWidget(self.invocations_Box)

        col3Layout.addWidget(self.level6_Slots)
        col3Layout.addWidget(self.level7_Slots)
        col3Layout.addWidget(self.level8_Slots)
        col3Layout.addWidget(self.level9_Slots)

        self.layout.addLayout(header_Layout,0,0,1,self.layout.columnCount())
        self.layout.addWidget(ELine(),      1,0,1,self.layout.columnCount(),Qt.AlignTop)

    def setSizes(self):
        font = qApp.font()
        size = font.pointSize()
        self.default_FS = size # 8
        self.small_FS = size - math.ceil(size/8) # 7
        self.middle_FS = size + math.floor(size/5) # 9
        self.medium_FS = size + math.ceil(size/4) # 10
        self.big_FS = size + math.ceil(size/2) # 14
        self.large_FS = size * 2 # 16
        self.huge_FS = math.ceil(size * 2.5)

class ELine(QFrame):
    def __init__(self, vertical=False):
        super().__init__()
        if vertical:
            self.setFrameShape(QFrame.VLine)
        else:
            self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
