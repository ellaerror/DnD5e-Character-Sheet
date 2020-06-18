from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random, math, copy
from EClass import *
from ERace import *
from EBackground import *
from EFeature import *
from ECharacter import *
from EWidget import *

class EMainWidget(QWidget):

    characterChanged = pyqtSignal(ECharacter)
    spellListsMade = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.classes = importClasses("Vars\\classes.csv")
        importSubclasses("Vars\\subclasses.csv",self.classes)
        self.backgrounds = importBackgrounds("Vars\\backgrounds.csv")
        self.races = importRaces("Vars\\races2.csv")
        self.pactboons = importClassFeatures("Vars\\pacts.tsv")
        self.parentraces = []
        for r in self.races:
            if r.parent not in self.parentraces:
                self.parentraces.append(r.parent)

        self.currentClass = copy.deepcopy(self.classes[0])
        self.currentSubclass = copy.deepcopy(self.currentClass.subclasses[0])
        self.currentSubrace = copy.deepcopy(self.races[0])
        self.currentRace = copy.deepcopy(self.currentSubrace.parent)
        self.currentBackground = copy.deepcopy(self.backgrounds[0])
        self.currentCharacter = ECharacter(self.currentSubrace,self.currentClass,self.currentSubclass,self.currentBackground)

        self.customProfs = []
        self.customEquip = []
        self.filename = None

        self.setSizes()
        self.initUI()

    def initUI(self):
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        #
        # HEADER BOX
        #
        self.headerBox = QGridLayout()

        self.name_Edit = QLineEdit(self.currentCharacter.name)
        font = self.name_Edit.font()
        font.setPointSize(self.large_FS)
        self.name_Edit.setFont(font)
        self.name_Edit.setFixedHeight(46)
        self.name_Edit.editingFinished.connect(lambda: self.currentCharacter.setName(self.name_Edit.text()))

        self.class_Combo = QComboBox()
        for c in self.classes:
            self.class_Combo.addItem(c.name)
        self.class_Combo.currentIndexChanged.connect(self.updateSubclasses)
        self.class_Combo.currentIndexChanged.connect(self.updateClassValues)
        self.class_Combo.currentIndexChanged.connect(self.updateClassLists)
        self.class_Combo.currentIndexChanged.connect(self.updateSavingThrows)

        self.subclass_Combo = QComboBox()
        self.subclass_Combo.setMinimumWidth(180)
        self.updateSubclasses()
        self.subclass_Combo.currentIndexChanged.connect(self.updateCurrents)
        self.subclass_Combo.currentIndexChanged.connect(self.updateFeatures)
        self.subclass_Combo.currentIndexChanged.connect(self.updateSubclassLists)

        self.parentrace_Combo = QComboBox()
        for r in self.parentraces:
            self.parentrace_Combo.addItem(r)
        self.parentrace_Combo.currentIndexChanged.connect(self.updateSubraces)

        self.subrace_Combo = QComboBox()
        self.updateSubraces()
        self.subrace_Combo.currentIndexChanged.connect(self.updateCurrents)
        self.subrace_Combo.currentIndexChanged.connect(self.updateFeatures)
        self.subrace_Combo.currentIndexChanged.connect(self.updateRaceLists)
        self.subrace_Combo.currentIndexChanged.connect(self.updateAbilityScores)
        self.subrace_Combo.currentIndexChanged.connect(self.updateSpeed)

        self.background_Combo = QComboBox()
        for b in self.backgrounds:
            self.background_Combo.addItem(b.name)
        self.background_Combo.currentIndexChanged.connect(self.updateCurrents)
        self.background_Combo.currentIndexChanged.connect(self.updateFeatures)
        self.background_Combo.currentIndexChanged.connect(self.updateBackgroundLists)

        self.level_Edit = QLineEdit(str(self.currentCharacter.level))
        self.level_Edit.setFixedWidth(22)
        self.level_Edit.setValidator(QIntValidator())
        self.level_Edit.editingFinished.connect(lambda: self.currentCharacter.setLevel(int(self.level_Edit.text())))
        self.level_Edit.editingFinished.connect(self.updateCurrents)
        self.level_Edit.editingFinished.connect(self.updateAll)

        self.exp_Edit = QLineEdit("0")
        self.exp_Edit.setFixedWidth(50)
        self.exp_Edit.setValidator(QIntValidator())
        self.exp_Edit.editingFinished.connect(lambda: self.currentCharacter.setExp(int(self.exp_Edit.text())))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.headerBox.addWidget(self.name_Edit,          0,0,2,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Class"),         0,1,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.class_Combo,        0,2,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Subclass"),      0,3,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.subclass_Combo,     0,4,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Level"),         0,5,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.level_Edit,         0,6,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("EXP"),           0,7,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.exp_Edit,           0,8,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Race"),          1,1,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.parentrace_Combo,   1,2,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Subrace"),       1,3,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.subrace_Combo,      1,4,1,1,Qt.AlignTop)
        self.headerBox.addWidget(QLabel("Background"),    1,5,1,1,Qt.AlignVCenter)
        self.headerBox.addWidget(self.background_Combo,   1,6,1,3,Qt.AlignTop)

        #
        # ABILITY SCORES
        #

        self.abilityScoreLayout = QGridLayout()
        self.abilityScoreLayout.setVerticalSpacing(1)
        self.abilityScoreLayout.setHorizontalSpacing(1)
        self.abilityScoreLayout.setContentsMargins(4,4,4,4)

        self.abilityScoreBox = QGroupBox()
        self.abilityScoreBox.setLayout(self.abilityScoreLayout)

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
        groupBoxStyleSheet_NoTitle = """
        QGroupBox {
            border: 1px solid gray;
            padding: 0px 0px 0px 0px;
            margin: 0px 0px 0px 0px;
        }
        """

        self.abilityScoreBox.setStyleSheet(groupBoxStyleSheet_NoTitle)

        self.strMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)
        self.dexMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)
        self.conMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)
        self.intMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)
        self.wisMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)
        self.chrMod_Label = ELabel("+0",self.huge_FS,bold=True,width=62,height=62)

        self.strScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.strScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.strRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.strScore_Label  = ELabel("10",self.small_FS,width=20)

        self.dexScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.dexScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.dexScore_Edit.editingFinished.connect(self.updateArmorClass)
        self.dexRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.dexScore_Label  = ELabel("10",self.small_FS,width=20)

        self.conScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.conScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.conScore_Edit.editingFinished.connect(self.updateClassValues)
        self.conRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.conScore_Label  = ELabel("10",self.small_FS,width=20)

        self.intScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.intScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.intRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.intScore_Label  = ELabel("10",self.small_FS,width=20)

        self.wisScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.wisScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.wisRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.wisScore_Label  = ELabel("10",self.small_FS,width=20)

        self.chrScore_Edit   = ELineEdit("10",self.small_FS,width=20)
        self.chrScore_Edit.editingFinished.connect(self.updateAbilityScores)
        self.chrRaceMod_Label= ELabel("+0",self.small_FS,width=20)
        self.chrScore_Label  = ELabel("10",self.small_FS,width=20)

        self.abilityScoreLayout.addWidget(QLabel("Strength"),    0,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.strMod_Label,     1,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.strScore_Edit,    2,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.strRaceMod_Label, 2,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.strScore_Label,   2,2,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(QLabel("Dexterity"),   3,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.dexMod_Label,     4,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.dexScore_Edit,    5,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.dexRaceMod_Label, 5,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.dexScore_Label,   5,2,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(QLabel("Constitution"),6,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.conMod_Label,     7,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.conScore_Edit,    8,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.conRaceMod_Label, 8,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.conScore_Label,   8,2,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(QLabel("Intelligence"),9,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.intMod_Label,     10,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.intScore_Edit,    11,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.intRaceMod_Label, 11,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.intScore_Label,   11,2,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(QLabel("Wisdom"),      12,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.wisMod_Label,     13,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.wisScore_Edit,    14,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.wisRaceMod_Label, 14,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.wisScore_Label,   14,2,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(QLabel("Charisma"),    15,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.chrMod_Label,     16,0,1,3,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.chrScore_Edit,    17,0,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.chrRaceMod_Label, 17,1,1,1,Qt.AlignHCenter)
        self.abilityScoreLayout.addWidget(self.chrScore_Label,   17,2,1,1,Qt.AlignHCenter)

        #
        # PROFICIENCY BONUS
        #

        pb_Box = QGroupBox()
        pb_Box.setStyleSheet(groupBoxStyleSheet_NoTitle)
        pb_Layout = QGridLayout()
        pb_Layout.setContentsMargins(4,4,4,4)
        pb_Layout.setVerticalSpacing(2)
        pb_Layout.setHorizontalSpacing(4)
        pb_Box.setLayout(pb_Layout)

        self.pb_Edit = ELabel("+2",self.large_FS,bold=True,width=42,height=42)
        pb_Label = ELabel("Proficiency Bonus",fontSize=self.medium_FS,add=False)
        pb_Layout.addWidget(self.pb_Edit,0,0)
        pb_Layout.addWidget(pb_Label,0,1)

        pb_Box.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)

        #
        # INSPIRATION
        #

        inspiration_Box = QGroupBox()
        inspiration_Box.setStyleSheet(groupBoxStyleSheet_NoTitle)
        inspiration_Layout = QGridLayout()
        inspiration_Layout.setContentsMargins(4,4,4,4)
        inspiration_Layout.setVerticalSpacing(2)
        inspiration_Layout.setHorizontalSpacing(4)
        inspiration_Box.setLayout(inspiration_Layout)

        inspiration_Edit = ELineEdit("0",bold=True,width=42,height=42)
        inspiration_Label = ELabel("Inspiration",fontSize=self.medium_FS,add=False)
        inspiration_Layout.addWidget(inspiration_Edit,0,0)
        inspiration_Layout.addWidget(inspiration_Label,0,1)

        inspiration_Box.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)

        #
        # SAVING THROW
        #

        savingThrowBox = QGroupBox("Saving Throws")
        savingThrowBox.setStyleSheet(groupBoxStyleSheet)
        savingThrowLayout = QGridLayout()
        savingThrowLayout.setContentsMargins(4,4,4,4)
        savingThrowLayout.setSpacing(2)
        savingThrowBox.setLayout(savingThrowLayout)

        self.strSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)
        self.dexSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)
        self.conSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)
        self.intSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)
        self.wisSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)
        self.chrSavingThrow_Label = ELabel("+0",add=False,fontSize=self.medium_FS,width=30,alignment=Qt.AlignCenter)

        self.strSavingThrow_Prof = ECheckBox(True)
        self.dexSavingThrow_Prof = ECheckBox(True)
        self.conSavingThrow_Prof = ECheckBox(True)
        self.intSavingThrow_Prof = ECheckBox(True)
        self.wisSavingThrow_Prof = ECheckBox(True)
        self.chrSavingThrow_Prof = ECheckBox(True)

        self.savingThrowsList = [
            self.strSavingThrow_Prof,
            self.dexSavingThrow_Prof,
            self.conSavingThrow_Prof,
            self.intSavingThrow_Prof,
            self.wisSavingThrow_Prof,
            self.chrSavingThrow_Prof
        ]
        for box in self.savingThrowsList:
            box.stateChanged.connect(self.updateSavingThrows)

        savingThrowLayout.addWidget(self.strSavingThrow_Prof, 0,0)
        savingThrowLayout.addWidget(self.strSavingThrow_Label,0,1)
        savingThrowLayout.addWidget(QLabel("Strength"),       0,2,Qt.AlignLeft)
        savingThrowLayout.addWidget(self.dexSavingThrow_Prof, 1,0)
        savingThrowLayout.addWidget(self.dexSavingThrow_Label,1,1)
        savingThrowLayout.addWidget(QLabel("Dexterity"),      1,2,Qt.AlignLeft)
        savingThrowLayout.addWidget(self.conSavingThrow_Prof, 2,0)
        savingThrowLayout.addWidget(self.conSavingThrow_Label,2,1)
        savingThrowLayout.addWidget(QLabel("Constitution"),   2,2,Qt.AlignLeft)
        savingThrowLayout.addWidget(self.intSavingThrow_Prof, 3,0)
        savingThrowLayout.addWidget(self.intSavingThrow_Label,3,1)
        savingThrowLayout.addWidget(QLabel("Intelligence"),   3,2,Qt.AlignLeft)
        savingThrowLayout.addWidget(self.wisSavingThrow_Prof, 4,0)
        savingThrowLayout.addWidget(self.wisSavingThrow_Label,4,1)
        savingThrowLayout.addWidget(QLabel("Wisdom"),         4,2,Qt.AlignLeft)
        savingThrowLayout.addWidget(self.chrSavingThrow_Prof, 5,0)
        savingThrowLayout.addWidget(self.chrSavingThrow_Label,5,1)
        savingThrowLayout.addWidget(QLabel("Charisma"),       5,2,Qt.AlignLeft)

        savingThrowLayout.setColumnStretch(2,1)

        savingThrowBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)

        #
        # PHSYICAL ATTRIBUTES
        #

        self.physicalBox = QGroupBox()
        self.physicalLayout = QGridLayout()
        self.physicalLayout.setContentsMargins(4,4,4,4)
        self.physicalLayout.setSpacing(4)
        self.physicalBox.setLayout(self.physicalLayout)
        self.physicalBox.setStyleSheet(groupBoxStyleSheet_NoTitle)

        self.armorClass_Label  = ELineEdit(str(10+self.currentCharacter.getMod(1)),self.huge_FS,bold=True,width=70,height=60)
        self.armorClass_Label.setValidator(QIntValidator())
        self.armorClass_Label.editingFinished.connect(lambda: self.currentCharacter.setArmorClass(int(self.armorClass_Label.text())))

        self.initiative_Label  = ELineEdit(self.currentCharacter.getModString(1),  self.huge_FS,bold=True,width=70,height=60)
        self.initiative_Label.setValidator(QRegExpValidator(QRegExp(r"-{0,1}\+{0,1}[0-9]*")))
        self.initiative_Label.editingFinished.connect(lambda: self.currentCharacter.setInitiative(int(self.initiative_Label.text().strip("+ "))))

        self.speed_Label       = ELineEdit(str(self.currentSubrace.speed)+"ft",    self.huge_FS,bold=True,width=70,height=60)
        self.speed_Label.setValidator(QRegExpValidator(QRegExp(r"[0-9]*ft")))
        self.speed_Label.editingFinished.connect(lambda: self.currentCharacter.setSpeed(int(self.speed_Label.text().strip("ft "))))

        self.physicalLayout.addWidget(self.armorClass_Label,0,0,1,1,Qt.AlignLeft|Qt.AlignTop)
        self.physicalLayout.addWidget(QLabel("Armor Class"),1,0,1,1,Qt.AlignLeft|Qt.AlignTop)
        self.physicalLayout.addWidget(self.initiative_Label,0,1,1,1,Qt.AlignHCenter|Qt.AlignTop)
        self.physicalLayout.addWidget(QLabel("Initiative"), 1,1,1,1,Qt.AlignHCenter|Qt.AlignTop)
        self.physicalLayout.addWidget(self.speed_Label,     0,2,1,1,Qt.AlignRight|Qt.AlignTop)
        self.physicalLayout.addWidget(QLabel("Speed"),      1,2,1,1,Qt.AlignRight|Qt.AlignTop)

        maxHp_Layout = QHBoxLayout()

        self.maxHp_Edit = ELineEdit(str(self.currentCharacter.maxHp),fontSize=self.medium_FS,background=QPalette.Window,frame=True,height=20, width=140)
        self.maxHp_Edit.setAlignment(Qt.AlignLeft)
        self.maxHp_Edit.setValidator(QIntValidator())
        self.maxHp_Edit.editingFinished.connect(lambda: self.currentCharacter.setMaxHp(int(self.maxHp_Edit.text())))
        maxHp_Layout.addWidget(QLabel("Hit Point Maximum:"))
        maxHp_Layout.addWidget(self.maxHp_Edit)

        self.currentHp_Edit = ELineEdit(str(self.currentCharacter.maxHp),bold=True,fontSize=self.large_FS,height=60,width=240)
        self.currentHp_Edit.setValidator(QIntValidator())
        self.currentHp_Edit.editingFinished.connect(lambda: self.currentCharacter.setCurHp(int(self.currentHp_Edit.text())))
        currentHp_Label = ELabel("Current Hit Points",add=False,fontSize=self.default_FS)

        self.tempHp_Edit = ELineEdit("0",bold=True,fontSize=self.large_FS,height=60,width=240)
        tempHp_Label = ELabel("Temporary Hit Points",add=False,fontSize=self.default_FS)

        self.physicalLayout.addLayout(maxHp_Layout,       2,0,1,3)
        self.physicalLayout.addWidget(self.currentHp_Edit,3,0,1,3,Qt.AlignHCenter)
        self.physicalLayout.addWidget(currentHp_Label,    4,0,1,3,Qt.AlignHCenter)
        self.physicalLayout.addWidget(self.tempHp_Edit,   5,0,1,3,Qt.AlignHCenter)
        self.physicalLayout.addWidget(tempHp_Label,       6,0,1,3,Qt.AlignHCenter)

        # HIT DICE

        hitDiceLayout = QGridLayout()
        hitDiceLayout.setSpacing(2)
        hitDiceLayout.setContentsMargins(4,4,4,6)
        hitDiceBox = QGroupBox("Hit Dice")
        hitDiceBox.setLayout(hitDiceLayout)
        hitDiceBox.setStyleSheet(groupBoxStyleSheet)

        totalHd_Label = ELabel("Total:",fontSize=self.default_FS,add=False)
        totalHd_Label.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)

        self.maxHitDice_Label = ELabel(str(self.currentCharacter.level)+"d"+str(self.currentClass.hitDie)+self.currentCharacter.getModString(2),fontSize=8,add=False)
        self.maxHitDice_Label.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)

        self.hitDice_Edit = ELineEdit(str(self.currentCharacter.level),fontSize=self.medium_FS,width=40)

        hitDiceLayout.addWidget(totalHd_Label,        0,0, Qt.AlignLeft)
        hitDiceLayout.addWidget(self.maxHitDice_Label,0,1, Qt.AlignHCenter)
        hitDiceLayout.addWidget(self.hitDice_Edit,    1,0,1,2,Qt.AlignHCenter)

        # DEATH SAVES

        deathSaveLayout = QGridLayout()
        deathSaveLayout.setSpacing(2)
        deathSaveLayout.setContentsMargins(4,4,4,6)
        deathSaveBox = QGroupBox("Death Saves")
        deathSaveBox.setLayout(deathSaveLayout)
        deathSaveBox.setStyleSheet(groupBoxStyleSheet)

        succ_Label = ELabel("Successes",fontSize=self.default_FS,add=False)
        fail_Label = ELabel("Failures", fontSize=self.default_FS,add=False)

        deathSaveLayout.addWidget(succ_Label, 0,0,Qt.AlignLeft)
        deathSaveLayout.addWidget(fail_Label, 1,0,Qt.AlignLeft)
        deathSaveLayout.addWidget(QCheckBox(),0,1,Qt.AlignRight)
        deathSaveLayout.addWidget(QCheckBox(),0,2,Qt.AlignRight)
        deathSaveLayout.addWidget(QCheckBox(),0,3,Qt.AlignRight)
        deathSaveLayout.addWidget(QCheckBox(),1,1,Qt.AlignRight)
        deathSaveLayout.addWidget(QCheckBox(),1,2,Qt.AlignRight)
        deathSaveLayout.addWidget(QCheckBox(),1,3,Qt.AlignRight)

        addlLayout = QHBoxLayout()
        addlLayout.addWidget(hitDiceBox)
        addlLayout.addWidget(deathSaveBox)

        self.physicalLayout.addLayout(addlLayout, 7,0,1,3)
        self.physicalBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        #
        # FEATURES AND TRAITS
        #

        self.features_List = EFeatureView()

        font = self.features_List.font()
        font.setPointSize(self.middle_FS)
        self.features_List.setFont(font)

        self.features_List.setMinimumWidth(280)
        self.features_List.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.features_Model = EItemModel(parent=self.features_List)

        self.expandFeatures = QPushButton("Expand")
        self.expandFeatures.setFixedWidth(70)
        self.expandFeatures.clicked.connect(self.features_List.expandAll)

        self.collapseFeatures = QPushButton("Collapse")
        self.collapseFeatures.clicked.connect(self.features_List.collapseAll)
        self.collapseFeatures.setFixedWidth(70)

        featureBox = QGroupBox("Features && Traits")
        featureLayout = QGridLayout()
        featureLayout.setContentsMargins(4,4,4,4)
        featureBox.setLayout(featureLayout)
        featureBox.setStyleSheet(groupBoxStyleSheet)
        featureLayout.addWidget(self.features_List,0,0,1,3)
        featureLayout.addWidget(self.collapseFeatures,1,0,1,1,Qt.AlignLeft)
        featureLayout.addWidget(self.expandFeatures,1,2,1,1,Qt.AlignRight)

        #
        # PERSONALITY BOX
        #
        personality_Layout = QVBoxLayout()
        personality_Layout.setContentsMargins(4,4,4,4)
        personality_Layout.setSpacing(2)

        personality_Box = QGroupBox()
        personality_Box.setStyleSheet(groupBoxStyleSheet_NoTitle)
        personality_Box.setLayout(personality_Layout)

        self.traits = ELabeledEdit("Personality Traits")
        self.traits.edit.textChanged.connect(lambda: self.currentCharacter.setTraits(self.traits.edit.toPlainText()))
        self.ideals = ELabeledEdit("Ideals")
        self.ideals.edit.textChanged.connect(lambda: self.currentCharacter.setIdeals(self.ideals.edit.toPlainText()))
        self.bonds  = ELabeledEdit("Bonds")
        self.bonds.edit.textChanged.connect(lambda: self.currentCharacter.setBonds(self.bonds.edit.toPlainText()))
        self.flaws  = ELabeledEdit("Flaws")
        self.flaws.edit.textChanged.connect(lambda: self.currentCharacter.setFlaws(self.flaws.edit.toPlainText()))

        personality_Layout.addWidget(self.traits)
        personality_Layout.addWidget(self.ideals)
        personality_Layout.addWidget(self.bonds)
        personality_Layout.addWidget(self.flaws)

        personality_Box.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)

        #
        # SKILL PROFICIENCIES
        #

        skillProf_Layout = QGridLayout()
        skillProf_Layout.setVerticalSpacing(2)
        skillProf_Layout.setContentsMargins(4,4,4,4)
        skillProf_Layout.setHorizontalSpacing(2)
        skillProf_Box = QGroupBox("Skills")
        skillProf_Box.setLayout(skillProf_Layout)
        skillProf_Box.setStyleSheet(groupBoxStyleSheet)

        self.skillProfs = []
        self.skillExperts = []
        self.skillMods = []
        self.skillNames = [
            "Acrobatics (Dex)",
            "Animal Handling (Wis)",
            "Arcana (Int)",
            "Athletics (Str)",
            "Deception (Cha)",
            "History (Int)",
            "Insight (Wis)",
            "Intimidation (Cha)",
            "Investigation (Int)",
            "Medicine (Wis)",
            "Nature (Int)",
            "Perception (Wis)",
            "Performance (Cha)",
            "Persuasion (Cha)",
            "Religion (Int)",
            "Sleight of Hand (Dex)",
            "Stealth (Dex)",
            "Survival (Wis)"
        ]
        self.skillKey = [1,4,3,0,5,3,4,5,3,4,3,4,5,5,3,1,1,4]

        for row in range(0,18):
            self.skillProfs.append(ECheckBox())
            self.skillExperts.append(ECheckBox(size=10))
            self.skillMods.append(ELabel(self.currentCharacter.getModString(self.skillKey[row]),fontSize=self.medium_FS,add=False,width=25,alignment=Qt.AlignCenter))
            skillProf_Layout.addWidget(self.skillExperts[-1],row,0,Qt.AlignCenter)
            skillProf_Layout.addWidget(self.skillProfs[-1],  row,1,Qt.AlignVCenter)
            skillProf_Layout.addWidget(self.skillMods[-1],   row,2)
            skillProf_Layout.addWidget(ELabel(self.skillNames[row],fontSize=self.default_FS,add=False),row,3)

        for num in range(0,18):
            self.skillProfs[num].stateChanged.connect(self.updateSkills)
            self.skillExperts[num].stateChanged.connect(self.updateSkills)
            self.skillExperts[num].setEnabled(False)

        self.skillProfs[11].stateChanged.connect(self.updatePassiveWisdom)
        self.skillExperts[11].stateChanged.connect(self.updatePassiveWisdom)

        skillProf_Layout.setColumnStretch(3,1)

        #
        # PASSIVE WISDOM
        #

        passiveWis_Layout = QGridLayout()
        passiveWis_Layout.setContentsMargins(4,4,4,4)
        passiveWis_Layout.setSpacing(2)

        passiveWis_Box = QGroupBox()
        passiveWis_Box.setStyleSheet(groupBoxStyleSheet_NoTitle)
        passiveWis_Box.setLayout(passiveWis_Layout)

        self.passiveWis_Edit = ELineEdit("",bold=True,width=42,height=42)
        self.passiveWis_Edit.setReadOnly(True)
        passiveWis_Label = ELabel("Passive Wisdom (Perception)",fontSize=self.medium_FS,add=False,alignment=Qt.AlignCenter)
        passiveWis_Layout.addWidget(self.passiveWis_Edit,0,0)
        passiveWis_Layout.addWidget(passiveWis_Label,0,1)

        passiveWis_Box.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)

        self.updatePassiveWisdom()

        #
        # EQUIPMENT
        #

        equipment_Layout = QGridLayout()
        equipment_Layout.setContentsMargins(4,4,4,4)
        equipment_Layout.setSpacing(2)

        equipment_Box = QGroupBox("Equipment")
        equipment_Box.setStyleSheet(groupBoxStyleSheet)
        equipment_Box.setLayout(equipment_Layout)

        self.cp_Edit = ELabeledEdit("CP", 22, 60, scrollbars=False, enter=False)
        self.cp_Edit.setAlignment(Qt.AlignCenter)
        self.cp_Edit.setLeftAligned()
        self.cp_Edit.setPointSize(self.medium_FS)
        self.sp_Edit = ELabeledEdit("SP", 22, 60, scrollbars=False, enter=False)
        self.sp_Edit.setAlignment(Qt.AlignCenter)
        self.sp_Edit.setLeftAligned()
        self.sp_Edit.setPointSize(self.medium_FS)
        self.ep_Edit = ELabeledEdit("EP", 22, 60, scrollbars=False, enter=False)
        self.ep_Edit.setAlignment(Qt.AlignCenter)
        self.ep_Edit.setLeftAligned()
        self.ep_Edit.setPointSize(self.medium_FS)
        self.gp_Edit = ELabeledEdit("GP", 22, 60, scrollbars=False, enter=False)
        self.gp_Edit.setAlignment(Qt.AlignCenter)
        self.gp_Edit.setLeftAligned()
        self.gp_Edit.setPointSize(self.medium_FS)
        self.pp_Edit = ELabeledEdit("PP", 22, 60, scrollbars=False, enter=False)
        self.pp_Edit.setAlignment(Qt.AlignCenter)
        self.pp_Edit.setLeftAligned()
        self.pp_Edit.setPointSize(self.medium_FS)

        self.equipment_View = EEquipmentView()

        font = self.equipment_View.font()
        font.setPointSize(self.middle_FS)
        self.equipment_View.setFont(font)

        self.equipment_Model = EItemModel(root=["Item","Weight"], parent=self.equipment_View)
        self.equipment_View.setModel(self.equipment_Model)

        self.equipment_View.setMinimumWidth(self.equipment_View.sizeHint().width()-60)
        self.equipment_View.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

        self.addEquipment_Button = QPushButton("+")
        self.addEquipment_Button.setFixedWidth(22)
        self.addEquipment_Button.clicked.connect(self.addEquipment)

        self.delEquipment_Button = QPushButton("-")
        self.delEquipment_Button.setFixedWidth(22)
        self.delEquipment_Button.clicked.connect(self.delEquipment)

        equipment_Layout.addWidget(self.cp_Edit, 0,0, Qt.AlignLeft)
        equipment_Layout.addWidget(self.sp_Edit, 1,0, Qt.AlignLeft)
        equipment_Layout.addWidget(self.ep_Edit, 2,0, Qt.AlignLeft)
        equipment_Layout.addWidget(self.gp_Edit, 3,0, Qt.AlignLeft)
        equipment_Layout.addWidget(self.pp_Edit, 4,0, Qt.AlignLeft)
        equipment_Layout.addWidget(self.equipment_View,0,1,8,1)
        equipment_Layout.addWidget(self.addEquipment_Button,6,0,Qt.AlignRight|Qt.AlignBottom)
        equipment_Layout.addWidget(self.delEquipment_Button,7,0,Qt.AlignRight|Qt.AlignBottom)

        #
        # ATTACKS AND SPELLS
        #

        attack_Layout = QGridLayout()
        attack_Layout.setContentsMargins(4,4,4,4)
        attack_Layout.setSpacing(2)
        attack_Box = QGroupBox("Attacks && Spells")
        attack_Box.setStyleSheet(groupBoxStyleSheet)
        attack_Box.setLayout(attack_Layout)

        self.attack_View = EAttackView()

        font = self.attack_View.font()
        font.setPointSize(self.middle_FS)
        self.attack_View.setFont(font)

        self.attack_View.setMinimumWidth(240)
        self.attack_View.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.attack_Model = EItemModel(root=["Name","Atk Mod","Damage","Type"],parent=self.attack_View)
        self.attack_View.setModel(self.attack_Model)

        self.addAttack_Button = QPushButton("+")
        self.addAttack_Button.setFixedWidth(22)
        self.addAttack_Button.clicked.connect(self.addAttack)

        self.delAttack_Button = QPushButton("-")
        self.delAttack_Button.setFixedWidth(22)
        self.delAttack_Button.clicked.connect(self.delAttack)

        attack_Layout.addWidget(self.attack_View,0,0,1,2)

        attack_Layout.addWidget(self.delAttack_Button,1,0,Qt.AlignLeft)
        attack_Layout.addWidget(self.addAttack_Button,1,1,Qt.AlignRight)


        #
        # DRUID LAND BOX
        # fuck this i cant think of a better way to accomplish this
        #
        druidLand_Layout = QGridLayout()
        druidLand_Layout.setContentsMargins(0,0,0,0)
        druidLand_Layout.setSpacing(2)
        self.druidLand_Box = QGroupBox()
        self.druidLand_Box.setStyleSheet(groupBoxStyleSheet_NoTitle.replace("1px","0px"))
        self.druidLand_Box.setLayout(druidLand_Layout)

        self.druidLand_Combo = QComboBox()
        lands = ["Arctic","Coast","Desert","Forest","Grassland","Swamp","Mountain","Underdark"]
        for land in lands:
            self.druidLand_Combo.addItem(land)
        self.druidLand_Combo.currentIndexChanged.connect(lambda: self.currentCharacter.setDruidLand(self.druidLand_Combo.currentText()))
        self.druidLand_Combo.currentIndexChanged.connect(lambda: self.characterChanged.emit(self.currentCharacter))

        druidLand_Layout.addWidget(QLabel("Circle Land:"),0,0)
        druidLand_Layout.addWidget(self.druidLand_Combo,0,1)

        self.druidLand_Box.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Maximum)
        self.druidLand_Box.hide()

        #
        # WARLOCK PACT
        #
        warlockPact_Layout = QGridLayout()
        warlockPact_Layout.setContentsMargins(0,0,0,0)
        warlockPact_Layout.setSpacing(2)
        self.warlockPact_Box = QGroupBox()
        self.warlockPact_Box.setStyleSheet(groupBoxStyleSheet_NoTitle.replace("1px","0px"))
        self.warlockPact_Box.setLayout(warlockPact_Layout)

        self.warlockPact_Combo = QComboBox()
        self.warlockPact_Combo.currentIndexChanged.connect(self.updateCurrents)
        self.warlockPact_Combo.currentIndexChanged.connect(self.updateFeatures)
        for boon in self.pactboons:
            self.warlockPact_Combo.addItem(boon.name)

        warlockPact_Layout.addWidget(QLabel("Pact Boon:"),0,0)
        warlockPact_Layout.addWidget(self.warlockPact_Combo,0,1)

        self.warlockPact_Box.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Maximum)
        self.warlockPact_Box.hide()

        #
        # PROFICIENCIES & LANGUAGES
        #

        profLang_Layout = QGridLayout()
        profLang_Layout.setContentsMargins(4,4,4,4)
        profLang_Layout.setSpacing(2)
        profLang_Box = QGroupBox("Proficiencies && Languages")
        profLang_Box.setStyleSheet(groupBoxStyleSheet)
        profLang_Box.setLayout(profLang_Layout)

        self.profLang_View = EProfView()

        font = self.profLang_View.font()
        font.setPointSize(self.middle_FS)
        self.profLang_View.setFont(font)

        self.profLang_Model = EItemModel(root=["Type","Proficiency"],parent=self.profLang_View)
        self.profLang_View.setModel(self.profLang_Model)
        self.profLang_View.setMinimumHeight(250)

        self.addProfLang_Button = QPushButton("+")
        self.addProfLang_Button.setFixedWidth(22)
        self.addProfLang_Button.clicked.connect(self.addProfLang)

        self.delProfLang_Button = QPushButton("-")
        self.delProfLang_Button.setFixedWidth(22)
        self.delProfLang_Button.clicked.connect(self.delProfLang)

        profLang_Layout.addWidget(self.profLang_View,0,0,1,2)
        profLang_Layout.addWidget(self.delProfLang_Button,1,0,Qt.AlignLeft)
        profLang_Layout.addWidget(self.addProfLang_Button,1,1,Qt.AlignRight)

        #
        # MAIN LAYOUT
        #

        self.col1Layout = QVBoxLayout()
        self.col2Layout = QVBoxLayout()
        self.col3Layout = QVBoxLayout()
        self.col4Layout = QVBoxLayout()

        self.col1Layout.setSpacing(2)
        self.col2Layout.setSpacing(2)
        self.col3Layout.setSpacing(2)
        self.col4Layout.setSpacing(2)

        self.mainLayout.addLayout(self.col1Layout,2,0,Qt.AlignTop)
        self.mainLayout.addLayout(self.col2Layout,2,1,Qt.AlignTop)

        self.mainLayout.addWidget(passiveWis_Box,3,0,1,2,Qt.AlignTop)
        self.mainLayout.addWidget(profLang_Box,4,0,1,2,Qt.AlignTop)

        self.mainLayout.addLayout(self.col3Layout,2,2,3,1,Qt.AlignTop)
        self.mainLayout.addLayout(self.col4Layout,2,3,3,1,Qt.AlignTop)

        self.col1Layout.addWidget(self.abilityScoreBox,Qt.AlignTop)

        self.col2Layout.addWidget(inspiration_Box,Qt.AlignTop)
        self.col2Layout.addWidget(pb_Box,Qt.AlignTop)
        self.col2Layout.addWidget(savingThrowBox,Qt.AlignTop)
        self.col2Layout.addWidget(skillProf_Box,Qt.AlignTop)

        self.col3Layout.addWidget(self.physicalBox,Qt.AlignTop)
        self.col3Layout.addWidget(attack_Box,Qt.AlignTop)
        self.col3Layout.addWidget(equipment_Box,Qt.AlignTop)

        self.col4Layout.addWidget(personality_Box,Qt.AlignTop)
        self.col4Layout.addWidget(self.druidLand_Box,Qt.AlignTop)
        self.col4Layout.addWidget(self.warlockPact_Box,Qt.AlignTop)
        self.col4Layout.addWidget(featureBox,Qt.AlignTop)

        self.mainLayout.addLayout(self.headerBox,0,0,1,self.mainLayout.columnCount())
        self.mainLayout.addWidget(line,          1,0,1,self.mainLayout.columnCount(),Qt.AlignTop)

        self.updateFeatures()
        self.updateAbilityScores()
        self.updateClassValues()
        self.updateSavingThrows()
        self.updateBackgroundLists()
        self.updateSubclassLists()
        self.updateRaceLists()

        self.characterChanged.emit(self.currentCharacter)

    def updateSubraces(self):
        self.subrace_Combo.clear()
        parent = self.parentrace_Combo.currentText()
        for race in self.races:
            if race.parent == parent:
                self.subrace_Combo.addItem(race.name)

    def updateSubclasses(self):
        self.subclass_Combo.clear()
        for c in self.classes:
            if self.class_Combo.currentText() == c.name:
                current = c
        for s in current.subclasses:
            self.subclass_Combo.addItem(s.name)

    def updateCurrents(self):
        for c in self.classes:
            if c.name == self.class_Combo.currentText():
                self.currentClass = copy.deepcopy(c)
                self.currentCharacter.mainclass = copy.deepcopy(c)
                break

        if self.class_Combo.currentText() == "Warlock":
            if self.currentCharacter.level > 2:
                self.warlockPact_Box.show()
            for boon in self.pactboons:
                if boon.name == self.warlockPact_Combo.currentText():
                    self.currentCharacter.pactBoon = boon
        else:
            self.warlockPact_Box.hide()
            self.currentCharacter.pactBoon = None

        for s in self.currentClass.subclasses:
            if s.name == self.subclass_Combo.currentText():
                self.currentSubclass = copy.deepcopy(s)
                self.currentCharacter.subclass = copy.deepcopy(s)
                break

        if self.currentCharacter.subclass.basename == "land":
            self.druidLand_Box.show()
        else:
            self.druidLand_Box.hide()
            self.currentCharacter.druidLand = None

        for s in self.races:
            if s.name == self.subrace_Combo.currentText():
                self.currentSubrace = copy.deepcopy(s)
                self.currentCharacter.subrace = copy.deepcopy(s)
                break

        self.currentRace = self.currentSubrace.parent
        self.currentCharacter.parentrace = self.currentSubrace.parent

        for b in self.backgrounds:
            if b.name == self.background_Combo.currentText():
                self.currentBackground = copy.deepcopy(b)
                self.currentCharacter.background = copy.deepcopy(b)
                break

        self.characterChanged.emit(self.currentCharacter)

    def updateFeatures(self):
        self.features_Model.removeNonCustom()

        for level in range(0,int(self.level_Edit.text())):
            if level > 19:
                break
            for f in self.currentClass.features[level]:
                if len(f) > 1:
                    self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentClass.name+" "+str(level+1),f[1],source="Class"))
                elif len(f[0]) > 0:
                    self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentClass.name+" "+str(level+1),source="Class"))
            if self.class_Combo.currentText() == "Warlock" and level == 2:
                self.features_Model.appendRow(EFeatureItem(self.currentCharacter.pactBoon.name+":</b> Warlock 3",
                self.currentCharacter.pactBoon.description,
                source="Class"))
            for f in self.currentSubclass.features[level]:
                if len(f) > 1:
                    self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentSubclass.name+" "+str(level+1),f[1],source="Subclass"))
                elif len(f[0]) > 0:
                    self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentSubclass.name+" "+str(level+1),source="Subclass"))
        for f in self.currentSubrace.features:
            if len(f) > 1:
                self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentSubrace.name,f[1],source="Race"))
            elif len(f[0]) > 0:
                self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentSubrace.name,source="Race"))
        for f in self.currentBackground.features:
            self.features_Model.appendRow(EFeatureItem(f[0]+":</b> "+self.currentBackground.name+" Background",f[1],source="Background"))

        self.features_List.setModel(self.features_Model)

    def addFeature(self):
        dialog = FeatureDialog()
        dialog.exec_()
        if dialog.featureName:
            name = dialog.featureName + ":</b> " + dialog.sourceName
            self.features_Model.appendRow(EFeatureItem(name, dialog.htmlText, source="Custom"))
            self.features_List.expandAll()
            self.features_List.collapseAll()

    def updateClassLists(self):
        # Proficiencies
        self.profLang_Model.removeSource("Class")
        for key,value in self.currentCharacter.mainclass.proficiencies.items():
            for prof in value:
                if len(prof) > 0:
                    self.profLang_Model.appendRow(EBaseItem([key, prof.replace("|",", ").replace(":"," ")],edit=True,source="Class"))
        self.profLang_View.setModel(self.profLang_Model)

        # Equipment
        self.equipment_Model.removeSource("Class")
        for key in self.currentCharacter.mainclass.startingEquipment:
            if len(key) > 1:
                self.equipment_Model.appendRow(EBaseItem([" or ".join(key),"0"],edit=True,source="Class"))
            else:
                self.equipment_Model.appendRow(EBaseItem(key+["0"]))
        self.equipment_View.setModel(self.equipment_Model)
        self.equipment_View.expandAll()

    def updateSubclassLists(self):
        pass

    def updateRaceLists(self):
        # Proficiencies
        self.profLang_Model.removeSource("Race")
        for key,value in self.currentCharacter.subrace.proficiencies.items():
            for prof in value:
                if len(prof) > 0:
                    self.profLang_Model.appendRow(EBaseItem([key, prof],edit=True,source="Race"))
        for lang in self.currentCharacter.subrace.languages:
            self.profLang_Model.appendRow(EBaseItem(["Language", lang],edit=True,source="Race"))
        self.profLang_View.setModel(self.profLang_Model)

    def updateBackgroundLists(self):
        # Equipment
        self.equipment_Model.removeSource("Background")
        for item in self.currentCharacter.background.startingEquipment:
            self.equipment_Model.appendRow(EBaseItem([item,"0"],edit=True,source="Background"))
        self.equipment_Model.appendRow(EBaseItem([str(self.currentCharacter.background.gp)+"gp","0"],edit=True,source="Background"))
        self.equipment_View.setModel(self.equipment_Model)
        self.equipment_View.expandAll()

        # Proficiencies
        self.profLang_Model.removeSource("Background")
        for key,value in self.currentCharacter.background.proficiencies.items():
            for prof in value:
                if len(prof) > 0:
                    self.profLang_Model.appendRow(EBaseItem([key, prof],edit=True,source="Background"))
        for lang in range(0,self.currentCharacter.background.addLang):
            self.profLang_Model.appendRow(EBaseItem(["Language", "Choose one language"],edit=True,source="Background"))
        self.profLang_View.setModel(self.profLang_Model)

    def addProfLang(self):
        item = EBaseItem(["Armor","Light Armor"],source="Custom")
        item.setEditable(True)
        self.customProfs.append(item)
        self.profLang_Model.appendRow(item)
        self.profLang_View.setModel(self.profLang_Model)
        self.profLang_View.expandAll()

    def delProfLang(self):
        self.profLang_Model.removeRow(self.profLang_View.selectedIndexes()[0].row(), self.profLang_View.selectedIndexes()[0].parent())

    def addEquipment(self):
        item = EBaseItem(["Item Name","0"],source="Custom")
        item.setEditable(True)
        self.equipment_Model.appendRow(item)
        self.equipment_View.setModel(self.equipment_Model)
        self.equipment_View.expandAll()

    def delEquipment(self):
        self.equipment_Model.removeRow(self.equipment_View.selectedIndexes()[0].row(), self.equipment_View.selectedIndexes()[0].parent())

    def updateAbilityScores(self):
        self.currentCharacter.baseAbilityScores[0] = int(self.strScore_Edit.text())
        self.currentCharacter.baseAbilityScores[1] = int(self.dexScore_Edit.text())
        self.currentCharacter.baseAbilityScores[2] = int(self.conScore_Edit.text())
        self.currentCharacter.baseAbilityScores[3] = int(self.intScore_Edit.text())
        self.currentCharacter.baseAbilityScores[4] = int(self.wisScore_Edit.text())
        self.currentCharacter.baseAbilityScores[5] = int(self.chrScore_Edit.text())
        self.currentCharacter.updateAbilityScores()

        self.updatePassiveWisdom()

        self.strScore_Label.setText(str(self.currentCharacter.abilityScores[0]))
        self.dexScore_Label.setText(str(self.currentCharacter.abilityScores[1]))
        self.conScore_Label.setText(str(self.currentCharacter.abilityScores[2]))
        self.intScore_Label.setText(str(self.currentCharacter.abilityScores[3]))
        self.wisScore_Label.setText(str(self.currentCharacter.abilityScores[4]))
        self.chrScore_Label.setText(str(self.currentCharacter.abilityScores[5]))

        self.strRaceMod_Label.setText(self.currentCharacter.subrace.getModString(0))
        self.dexRaceMod_Label.setText(self.currentCharacter.subrace.getModString(1))
        self.conRaceMod_Label.setText(self.currentCharacter.subrace.getModString(2))
        self.intRaceMod_Label.setText(self.currentCharacter.subrace.getModString(3))
        self.wisRaceMod_Label.setText(self.currentCharacter.subrace.getModString(4))
        self.chrRaceMod_Label.setText(self.currentCharacter.subrace.getModString(5))

        self.strMod_Label.setText(self.currentCharacter.getModString(0))
        self.dexMod_Label.setText(self.currentCharacter.getModString(1))
        self.conMod_Label.setText(self.currentCharacter.getModString(2))
        self.intMod_Label.setText(self.currentCharacter.getModString(3))
        self.wisMod_Label.setText(self.currentCharacter.getModString(4))
        self.chrMod_Label.setText(self.currentCharacter.getModString(5))

        if self.currentCharacter.initiative == None:
            self.initiative_Label.setText(self.currentCharacter.getModString(1))
        else:
            if self.currentCharacter.initiative >= 0:
                string = "+"
            else:
                string = ""
            string += str(self.currentCharacter.initiative)
            self.initiative_Label.setText(string)

        self.updateArmorClass()
        self.updateSkills()

        self.characterChanged.emit(self.currentCharacter)

    def updateArmorClass(self):
        if self.currentCharacter.armorClass == None:
            baseAC = 10+self.currentCharacter.getMod(1)
            if self.currentCharacter.mainclass.name == "Monk":
                baseAC += self.currentCharacter.getMod(4)
            if self.currentCharacter.mainclass.name == "Barbarian":
                baseAC += self.currentCharacter.getMod(2)
            self.armorClass_Label.setText(str(baseAC))
        else:
            baseAC = self.currentCharacter.armorClass
            self.armorClass_Label.setText(str(baseAC))

    def updateSpeed(self):
        speed = self.currentCharacter.speed
        if self.currentCharacter.mainclass.name == "Monk" and self.currentCharacter.level > 1:
            speed += (math.floor((self.currentCharacter.level-2)/4)*5)+10
        if self.currentCharacter.mainclass.name == "Barbarian" and self.currentCharacter.level > 4:
            speed += 10
        self.speed_Label.setText(str(speed)+"ft")

    def updatePassiveWisdom(self):
        self.passiveWis_Edit.setText(str(10+self.currentCharacter.getMod(4)+(self.currentCharacter.pb*2 if self.skillProfs[11].isChecked() and self.skillExperts[11].isChecked() else self.currentCharacter.pb if self.skillProfs[11].isChecked() else 0)))

    def saveCurrentCharacter(self):
        if self.filename:
            file = open(self.filename,"w")
            #
            # MAIN CHARACTER PROPERTIES
            #
            file.write(self.currentCharacter.toLine()+"\n")
            file.write(self.currentCharacter.subrace.toLine()+"\n")
            file.write(self.currentCharacter.mainclass.toLine()+"\n")
            file.write(self.currentCharacter.subclass.toLine()+"\n")
            file.write(self.currentCharacter.background.toLine()+"\n")
            #
            # SKILL PROFICIENCIES
            #
            profs = []
            experts = []
            for prof in self.skillProfs:
                profs.append(prof.isChecked())
            for prof in self.skillExperts:
                experts.append(prof.isChecked())
            file.write(",".join(str(x) for x in profs)+"\n")
            file.write(",".join(str(x) for x in experts)+"\n")
            #
            # LISTS
            #
            file.write(self.equipment_Model.toLine()+"\n")
            file.write(self.profLang_Model.toLine()+"\n")
            file.write(self.attack_Model.toLine()+"\n")
            file.write(self.features_Model.toLine_f()+"\n")
            #
            # MONEY
            #
            file.write(self.cp_Edit.edit.toPlainText()+","+self.sp_Edit.edit.toPlainText()+","+self.ep_Edit.edit.toPlainText()+","+self.gp_Edit.edit.toPlainText()+","+self.pp_Edit.edit.toPlainText()+"\n")
            #
            # SPELLS
            #
            for spell in self.currentCharacter.spells:
                file.write(spell.toLine_C())
            file.write("SPELLS END")
            file.close()
        else:
            self.saveCurrentCharacterAs()

    def saveCurrentCharacterAs(self):
        filename, _ = QFileDialog.getSaveFileName(self,"Save Character","","Character File (*.csv)")
        if filename:
            self.filename = filename
            self.saveCurrentCharacter()

    def openCharacter(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Open Character","","Character File (*.csv)")
        if filename:
            file = open(filename, "r")
            #
            # CHARACTER VALUES
            #
            indexes = [0, 0, 0, 0, 0]
            charInfo = file.readline().strip().split(",")
            race = ERace.fromLine(file.readline())
            indexes[0] = self.parentraces.index(race.parent)
            subraces = []
            for r in self.races:
                if r.parent == race.parent:
                    subraces.append(r.name)
                if r.name == race.name:
                    race = copy.deepcopy(r)
                    break
            indexes[4] = subraces.index(race.name)
            mainclass = EClass.fromLine(file.readline())
            for c in self.classes:
                if c.name == mainclass.name:
                    mainclass = copy.deepcopy(c)
                    indexes[1] = self.classes.index(c)
                    break
            subclass = ESubclass.fromLine(file.readline())
            for s in mainclass.subclasses:
                if s.name == subclass.name:
                    subclass = copy.deepcopy(s)
                    indexes[2] = mainclass.subclasses.index(s)
                    break
            background = EBackground.fromLine(file.readline())
            for b in self.backgrounds:
                if b.name == background.name:
                    background = copy.deepcopy(b)
                    indexes[3] = self.backgrounds.index(b)
                    break
            scores = [int(charInfo[5]),int(charInfo[6]),int(charInfo[7]),int(charInfo[8]),int(charInfo[9]),int(charInfo[10])]
            newChar = ECharacter(race, mainclass, subclass, background,level=int(charInfo[1]),name=charInfo[0],abilityScores=scores)
            newChar.exp = int(charInfo[2])
            newChar.maxHp = int(charInfo[3])
            newChar.currentHp = int(charInfo[4])
            newChar.traits = charInfo[11]
            newChar.ideals = charInfo[12]
            newChar.bonds  = charInfo[13]
            newChar.flaws  = charInfo[14]
            newChar.armorClass = int(charInfo[15])
            newChar.initiative = int(charInfo[16])
            newChar.speed = int(charInfo[17])
            newChar.name = charInfo[0]

            self.parentrace_Combo.setCurrentIndex(indexes[0])
            self.class_Combo.setCurrentIndex(indexes[1])
            self.subclass_Combo.setCurrentIndex(indexes[2])
            self.background_Combo.setCurrentIndex(indexes[3])
            self.subrace_Combo.setCurrentIndex(indexes[4])

            #
            # PROFICIENCY VALUES
            #
            profValues = file.readline().strip().split(",")
            count = 0
            for value in profValues:
                if value == "True":
                    self.skillProfs[count].setCheckState(True)
                else:
                    self.skillProfs[count].setCheckState(False)
                count+=1
            expertValues = file.readline().strip().split(",")
            count = 0
            for value in expertValues:
                if value == "True":
                    self.skillExperts[count].setCheckState(True)
                else:
                    self.skillExperts[count].setCheckState(False)
                count+=1
            #
            # ITEM LISTS
            #
            equipList  = file.readline().strip().split(",")
            profList   = file.readline().strip().split(",")
            attackList = file.readline().strip().split(",")

            self.equipment_Model = EItemModel(root=["Item","Weight"], parent=self.equipment_View)
            for item in equipList:
                if len(item) > 0:
                    item = item.replace("$",",").split(";")
                    source = item[-1].split(":")[-1]
                    self.equipment_Model.appendRow(EBaseItem(item[:-1], edit=True, source=item[-1]))
            self.equipment_View.setModel(self.equipment_Model)
            self.equipment_View.expandAll()

            self.profLang_Model = EItemModel(root=["Type","Proficiency"],parent=self.profLang_View)
            for item in profList:
                if len(item) > 0:
                    item = item.replace("$",",").split(";")
                    source = item[-1].split(":")[-1]
                    self.profLang_Model.appendRow(EBaseItem(item[:-1], edit=True, source=item[-1]))
            self.profLang_View.setModel(self.profLang_Model)
            self.profLang_View.expandAll()

            self.attack_Model = EItemModel(root=["Name","Atk Mod","Damage","Type"],parent=self.attack_View)
            for item in attackList:
                if len(item) > 0:
                    item = item.replace("$",",").split(";")
                    self.attack_Model.appendRow(EBaseItem(item[:-1], edit=True, source=item[-1]))
            self.attack_View.setModel(self.attack_Model)
            self.attack_View.expandAll()
            #
            # FEATURE LIST
            #
            featureList = file.readline().strip().split(",")
            for item in featureList:
                if len(item) > 0:
                    item = item.replace("$",",").split(";")
                    feature = item[0].split(":")
                    source = item[-1]
                    name = feature[0].replace("~",":")
                    desc = feature[1].replace("~",":").replace("`",";")
                    self.features_Model.appendRow(EFeatureItem(name, desc, source=source))
            self.features_List.setModel(self.features_Model)
            self.features_List.expandAll()
            self.features_List.collapseAll()
            #
            # MONEY
            #
            money = file.readline().strip().split(",")
            self.cp_Edit.edit.setText(money[0])
            self.sp_Edit.edit.setText(money[1])
            self.ep_Edit.edit.setText(money[2])
            self.gp_Edit.edit.setText(money[3])
            self.pp_Edit.edit.setText(money[4])

            spellKeys = []
            spellData = file.readline().strip().split(",")
            while len(spellData) > 1:
                spellKeys.append(spellData)
                spellData = file.readline().strip().split(",")

            file.close()
            self.currentCharacter = newChar
            self.updateNewCharacterValues()

            self.spellListsMade.emit(spellKeys)

            self.filename = filename

    def updateNewCharacterValues(self):
        self.name_Edit.setText(self.currentCharacter.name)
        self.level_Edit.setText(str(self.currentCharacter.level))
        self.exp_Edit.setText(str(self.currentCharacter.exp))
        self.maxHp_Edit.setText(str(self.currentCharacter.maxHp))
        self.currentHp_Edit.setText(str(self.currentCharacter.currentHp))
        self.strScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[0]))
        self.dexScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[1]))
        self.conScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[2]))
        self.intScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[3]))
        self.wisScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[4]))
        self.chrScore_Edit.setText(str(self.currentCharacter.baseAbilityScores[5]))
        self.traits.edit.setPlainText(self.currentCharacter.getTraits())
        self.ideals.edit.setPlainText(self.currentCharacter.getIdeals())
        self.bonds.edit.setPlainText(self.currentCharacter.getBonds())
        self.flaws.edit.setPlainText(self.currentCharacter.getFlaws())
        self.updateCurrents()
        self.updateAll()

    def updateSavingThrows(self):
        self.strSavingThrow_Label.setText(self.currentCharacter.getModString(0,self.currentCharacter.pb if self.strSavingThrow_Prof.isChecked() else 0))
        self.dexSavingThrow_Label.setText(self.currentCharacter.getModString(1,self.currentCharacter.pb if self.dexSavingThrow_Prof.isChecked() else 0))
        self.conSavingThrow_Label.setText(self.currentCharacter.getModString(2,self.currentCharacter.pb if self.conSavingThrow_Prof.isChecked() else 0))
        self.intSavingThrow_Label.setText(self.currentCharacter.getModString(3,self.currentCharacter.pb if self.intSavingThrow_Prof.isChecked() else 0))
        self.wisSavingThrow_Label.setText(self.currentCharacter.getModString(4,self.currentCharacter.pb if self.wisSavingThrow_Prof.isChecked() else 0))
        self.chrSavingThrow_Label.setText(self.currentCharacter.getModString(5,self.currentCharacter.pb if self.chrSavingThrow_Prof.isChecked() else 0))

    def updateClassValues(self):
        self.maxHitDice_Label.setText(str(self.currentCharacter.level)+"d"+str(self.currentCharacter.mainclass.hitDie)+self.currentCharacter.getModString(2, mul=self.currentCharacter.level))
        self.hitDice_Edit.setText(str(self.currentCharacter.level))

        self.strSavingThrow_Prof.setCheckState("Strength" in self.currentCharacter.mainclass.savingThrows)
        self.dexSavingThrow_Prof.setCheckState("Dexterity" in self.currentCharacter.mainclass.savingThrows)
        self.conSavingThrow_Prof.setCheckState("Constitution" in self.currentCharacter.mainclass.savingThrows)
        self.intSavingThrow_Prof.setCheckState("Intelligence" in self.currentCharacter.mainclass.savingThrows)
        self.wisSavingThrow_Prof.setCheckState("Wisdom" in self.currentCharacter.mainclass.savingThrows)
        self.chrSavingThrow_Prof.setCheckState("Charisma" in self.currentCharacter.mainclass.savingThrows)

        self.pb_Edit.setText(self.currentCharacter.getPBString())

        self.currentCharacter.spells = []
        self.characterChanged.emit(self.currentCharacter)

        self.updateArmorClass()
        self.updateSpeed()

    def updateSkills(self):
        for num in range(0,18):
            self.skillMods[num].setText(self.currentCharacter.getModString(self.skillKey[num],self.currentCharacter.pb*2 if self.skillProfs[num].isChecked() and self.skillExperts[num].isChecked() else self.currentCharacter.pb if self.skillProfs[num].isChecked() else 0))
            if self.skillProfs[num].isChecked():
                self.skillExperts[num].setEnabled(True)
            else:
                self.skillExperts[num].setEnabled(False)

    def addAttack(self):
        item = EBaseItem(["Item Name","+0","1d4", "Slashing"],source="Custom")
        item.setEditable(True)
        self.attack_Model.appendRow(item)
        self.attack_View.setModel(self.attack_Model)
        self.attack_View.expandAll()

    def delAttack(self):
        self.attack_Model.removeRow(self.attack_View.selectedIndexes()[0].row(), self.attack_View.selectedIndexes()[0].parent())

    def updateAll(self):
        self.updateAbilityScores()
        self.updateSkills()
        self.updateClassValues()
        self.updateSavingThrows()
        self.updateSpeed()
        self.updateArmorClass()
        self.updateFeatures()

    def rollScores(self):
        self.statDialog = StatDialog(self)
        self.statDialog.exec_()
        if self.statDialog.scores:
            self.strScore_Edit.setText(str(self.statDialog.scores[0]))
            self.dexScore_Edit.setText(str(self.statDialog.scores[1]))
            self.conScore_Edit.setText(str(self.statDialog.scores[2]))
            self.intScore_Edit.setText(str(self.statDialog.scores[3]))
            self.wisScore_Edit.setText(str(self.statDialog.scores[4]))
            self.chrScore_Edit.setText(str(self.statDialog.scores[5]))
            self.updateAbilityScores()
            self.updateClassValues()

    def rollDice(self):
        self.diceDialog = RollDialog(self)
        self.diceDialog.show()

    def setSizes(self):
        font = qApp.font()
        size = font.pointSize()
        self.default_FS = size # 8
        self.small_FS = size - math.ceil(size/8) # 7
        self.middle_FS = size + math.floor(size/5) # 9
        self.medium_FS = size + math.ceil(size/4) # 10
        self.large_FS = size * 2 # 16
        self.huge_FS = math.ceil(size * 2.5)

class RollDialog(QDialog):
    def __init__(self, parent=None, amt=1, die=20, mod=0):
        super().__init__(parent)
        self.scores = None
        self.mainLayout = QGridLayout()
        self.setWindowTitle("Roll Dice")
        self.setLayout(self.mainLayout)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.roll_Button = QPushButton("Roll")
        self.roll_Button.clicked.connect(self.roll)

        self.amount_Edit = ELineEdit(str(amt), width=25, fontSize=8)
        self.amount_Edit.setValidator(QIntValidator())

        self.type_Edit = ELineEdit(str(die), width=25, fontSize=8)
        self.type_Edit.setValidator(QIntValidator())

        self.mod_Edit = ELineEdit(str(mod), width=25, fontSize=8)
        self.mod_Edit.setValidator(QIntValidator())

        self.result_Label = ELabel("", fontSize=20, width=75,height=75)

        self.math_Label = ELabel("",fontSize=8,add=False)
        self.math_Label.setWordWrap(True)

        self.mainLayout.addWidget(ELabel("Roll:",fontSize=8,add=False),0,0)
        self.mainLayout.addWidget(self.amount_Edit,0,1)
        self.mainLayout.addWidget(ELabel("d",fontSize=8,add=False),0,2)
        self.mainLayout.addWidget(self.type_Edit,0,3)
        self.mainLayout.addWidget(ELabel("+",fontSize=8,add=False),0,4)
        self.mainLayout.addWidget(self.mod_Edit,0,5)

        self.mainLayout.addWidget(self.roll_Button,0,6)

        self.mainLayout.addWidget(self.result_Label,1,6)
        self.mainLayout.addWidget(self.math_Label,1,0,1,6)

    def roll(self):
        amount = int(self.amount_Edit.text())
        dieType = int(self.type_Edit.text())
        mod = int(self.mod_Edit.text())
        values = []
        for num in range(0,amount):
            values.append(random.randrange(1,dieType+1,1))
        self.result_Label.setText(str(sum(values)+mod))

        math = " + ".join(str(x) for x in values)
        if mod != 0:
            math += " (+"+str(mod)+")"
        self.math_Label.setText(math)

class DragLabel(ELabel):
    def __init__(self, text=""):
        super().__init__(text,width=30,height=30)
        self.setAcceptDrops(True)
        if len(self.text()) > 0:
            self._Empty = False
        else:
            self._Empty = True
            self.empty()

    def isEmpty(self):
        return self._Empty

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isEmpty():
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.isEmpty():
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.text())
        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def empty(self):
        self._Empty = True
        self.setAutoFillBackground(False)
        self.setText("")
        self.setBackgroundRole(QPalette.Window)

    def fill(self):
        self._Empty = False
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Base)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and self.isEmpty():
            event.acceptProposedAction()

    def dropEvent(self, event):
        pos = event.pos()
        text = event.mimeData().text()
        self.setText(text)
        event.acceptProposedAction()
        event.source().empty()
        self.fill()

class FeatureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.htmlText = None
        self.featureName = None
        self.sourceName = None
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.mainLayout = QGridLayout()
        self.setWindowTitle("Add a Feature")
        self.setLayout(self.mainLayout)

        self.name_Edit = QLineEdit("Name")
        self.source_Edit = QLineEdit("Druid 1")
        self.feature_Edit = QTextEdit()

        self.exit_Button = QPushButton("Cancel")
        self.exit_Button.clicked.connect(self.close)
        self.save_Button = QPushButton("Save")
        self.save_Button.clicked.connect(self.saveClose)

        self.mainLayout.addWidget(QLabel("Feature Name:"),0,0)
        self.mainLayout.addWidget(self.name_Edit,0,1)
        self.mainLayout.addWidget(QLabel("Feature Source:"),1,0)
        self.mainLayout.addWidget(self.source_Edit,1,1)
        self.mainLayout.addWidget(QLabel("Feature Details"),2,0,1,2)
        self.mainLayout.addWidget(self.feature_Edit,3,0,1,2)
        self.mainLayout.addWidget(self.exit_Button,4,0)
        self.mainLayout.addWidget(self.save_Button,4,1)

    def saveClose(self):
        self.htmlText = self.feature_Edit.toPlainText().replace("\n","<br>")
        self.featureName = self.name_Edit.text()
        self.sourceName = self.source_Edit.text()
        self.close()

class StatDialog(QDialog):

    groupBoxStyleSheet_NoTitle = """
    QGroupBox {
        border: 1px solid gray;
        padding: 0px 0px 0px 0px;
        margin: 0px 0px 0px 0px;
    }
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scores = None
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.mainLayout = QGridLayout()
        self.setWindowTitle("Roll Ability Scores")
        self.setLayout(self.mainLayout)

        self.dice_Layout = QGridLayout()
        self.dice_Layout.setContentsMargins(3,3,3,3)
        self.dice_Layout.setSpacing(3)
        self.dice_Group = QGroupBox()
        self.dice_Group.setStyleSheet(self.groupBoxStyleSheet_NoTitle)
        self.dice_Group.setLayout(self.dice_Layout)

        self.statDice_Label = QLabel("Dice to Roll:")
        self.statDice = QLineEdit("4d6")
        self.statDice.setFixedWidth(50)
        self.statDice.setDragEnabled(False)
        self.statDice.setAcceptDrops(False)
        self.statDice.setValidator(QRegExpValidator(QRegExp(r"[0-9]*d[0-9]+[\+\-][0-9]*")))

        self.dropLowestDice = QCheckBox("Drop Lowest Dice")
        self.dropLowestDice.setChecked(True)

        self.rerollOnes = QCheckBox("Reroll Ones")
        self.rerollOnes.setChecked(True)

        self.roll_Button = QPushButton("Roll")
        self.roll_Button.clicked.connect(self.rollScores)
        self.roll_Button.setFixedWidth(120)
        self.save_Button = QPushButton("Use")
        self.save_Button.setFixedWidth(60)
        self.save_Button.clicked.connect(self.saveClose)
        self.exit_Button = QPushButton("Cancel")
        self.exit_Button.setFixedWidth(60)
        self.exit_Button.clicked.connect(self.close)

        self.dice_Layout.addWidget(self.statDice_Label,0,0)
        self.dice_Layout.addWidget(self.statDice,      0,1)
        self.dice_Layout.addWidget(self.dropLowestDice,1,0,1,2)
        self.dice_Layout.addWidget(self.rerollOnes,    2,0,1,2)
        self.dice_Layout.addWidget(self.roll_Button,   3,0,1,2)

        self.finalScores_Layout = QGridLayout()
        self.finalScores_Layout.setContentsMargins(3,3,3,3)
        self.finalScores_Layout.setSpacing(3)
        self.finalScores_Group = QGroupBox()
        self.finalScores_Group.setStyleSheet(self.groupBoxStyleSheet_NoTitle)
        self.finalScores_Group.setLayout(self.finalScores_Layout)

        str_Label = ELabel("STR",fontSize=10,add=False)
        dex_Label = ELabel("DEX",fontSize=10,add=False)
        con_Label = ELabel("CON",fontSize=10,add=False)
        int_Label = ELabel("INT",fontSize=10,add=False)
        wis_Label = ELabel("WIS",fontSize=10,add=False)
        cha_Label = ELabel("CHA",fontSize=10,add=False)

        self.str_Drop = DragLabel()
        self.str_Drop.empty()
        self.dex_Drop = DragLabel()
        self.dex_Drop.empty()
        self.con_Drop = DragLabel()
        self.con_Drop.empty()
        self.int_Drop = DragLabel()
        self.int_Drop.empty()
        self.wis_Drop = DragLabel()
        self.wis_Drop.empty()
        self.cha_Drop = DragLabel()
        self.cha_Drop.empty()

        self.finalScores_Layout.addWidget(str_Label, 0,0)
        self.finalScores_Layout.addWidget(dex_Label, 1,0)
        self.finalScores_Layout.addWidget(con_Label, 2,0)
        self.finalScores_Layout.addWidget(int_Label, 3,0)
        self.finalScores_Layout.addWidget(wis_Label, 4,0)
        self.finalScores_Layout.addWidget(cha_Label, 5,0)

        self.finalScores_Layout.addWidget(self.str_Drop, 0,1)
        self.finalScores_Layout.addWidget(self.dex_Drop, 1,1)
        self.finalScores_Layout.addWidget(self.con_Drop, 2,1)
        self.finalScores_Layout.addWidget(self.int_Drop, 3,1)
        self.finalScores_Layout.addWidget(self.wis_Drop, 4,1)
        self.finalScores_Layout.addWidget(self.cha_Drop, 5,1)

        self.scores_Layout = QGridLayout()
        self.scores_Layout.setContentsMargins(3,3,3,3)
        self.scores_Layout.setSpacing(3)
        self.scores_Group = QGroupBox()
        self.scores_Group.setStyleSheet(self.groupBoxStyleSheet_NoTitle)
        self.scores_Group.setLayout(self.scores_Layout)

        for row in range(0,2):
            for col in range(0,3):
                self.scores_Layout.addWidget(DragLabel(),row,col)

        self.stats_Layout = QGridLayout()
        self.stats_Layout.setContentsMargins(3,3,3,3)
        self.stats_Layout.setSpacing(3)
        self.stats_Group = QGroupBox()
        self.stats_Group.setStyleSheet(self.groupBoxStyleSheet_NoTitle)
        self.stats_Group.setLayout(self.stats_Layout)
        self.stats_Layout.addWidget(QLabel("Average Score:"),   0,0)
        self.stats_Layout.addWidget(QLabel("Total Points:"),    1,0)
        self.stats_Layout.addWidget(QLabel("Point Buy Points:"),2,0)

        self.avg_Label = QLabel()
        self.total_Label = QLabel()
        self.pointBuy_Label = QLabel()

        self.stats_Layout.addWidget(self.avg_Label,0,1)
        self.stats_Layout.addWidget(self.total_Label,1,1)
        self.stats_Layout.addWidget(self.pointBuy_Label,2,1)

        self.mainLayout.addWidget(self.dice_Group,       0,0,1,2)
        self.mainLayout.addWidget(self.scores_Group,     1,0,1,2)
        self.mainLayout.addWidget(self.finalScores_Group,0,2,4,1)
        self.mainLayout.addWidget(self.stats_Group,      2,0,1,2)
        self.mainLayout.addWidget(self.exit_Button,      3,0)
        self.mainLayout.addWidget(self.save_Button,      3,1)

    def rollScores(self):
        dice = self.statDice.text().split("d")
        if "+" in dice[-1]:
            dice = [dice[0]]+dice[-1].split("+")
        elif "-" in dice[-1]:
            dice = [dice[0]]+dice[-1].split("-")
            dice[-1] = int(dice[-1])*-1
        else:
            dice.append(0)
        if len(dice) < 3:
            return
        for num in range(0,len(dice)):
            dice[num] = int(dice[num])

        scores = self.getStats(dice[0],dice[1],dice[2],self.dropLowestDice.isChecked(),self.rerollOnes.isChecked())
        count = 0
        for row in range(0,2):
            for col in range(0,3):
                item = self.scores_Layout.itemAtPosition(row,col).widget()
                self.scores_Layout.removeWidget(item)
                item.empty()
                del item
                self.scores_Layout.addWidget(DragLabel(str(scores[count])),row,col)
                count+=1

        self.avg_Label.setText(str(round(sum(scores)/6,2)))
        self.total_Label.setText(str(sum(scores)))
        total = 0
        for score in scores:
            if score <= 3:
                total -= 9
            elif score == 4:
                total -= 6
            elif score == 5:
                total -= 4
            elif score < 14 and score > 5:
                total += score - 8
            elif score == 14:
                total += 7
            elif score == 15:
                total += 9
            elif score == 16:
                total += 12
            elif score == 17:
                total += 15
            else:
                total += 19
        self.pointBuy_Label.setText(str(total))

        self.str_Drop.empty()
        self.dex_Drop.empty()
        self.con_Drop.empty()
        self.int_Drop.empty()
        self.wis_Drop.empty()
        self.cha_Drop.empty()

    def getStats(self, numDice=4, die=6, mod=0, drop=True, rerollOnes=False):
        finalList=[]
        if rerollOnes:
            min = 2
        else:
            min = 1
        for num in range(0,6):
            list = []
            for num2 in range(0,numDice):
                list.append(random.randrange(min,die+1,1)+mod)
            list.sort()
            if drop:
                finalList.append(sum(list[1:]))
            else:
                finalList.append(sum(list))
        finalList.sort()
        return finalList

    def saveClose(self):
        scores = []
        try:
            scores.append(int(self.str_Drop.text()))
            scores.append(int(self.dex_Drop.text()))
            scores.append(int(self.con_Drop.text()))
            scores.append(int(self.int_Drop.text()))
            scores.append(int(self.wis_Drop.text()))
            scores.append(int(self.cha_Drop.text()))
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("All ability scores must be selected in order to import them into character sheet.\nDrag and drop all of the rolled scores to your chosen ability in order to import them into the program.")
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        self.scores = scores
        self.close()

class EScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setWidgetResizable(True)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def resizeEvent(self, e):
        super().resizeEvent(e)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("D&D5e Character Sheet")
        qApp.setPalette(self.style().standardPalette())

        self.mainWidget = EMainWidget(parent=self)

        self.scrollWidget = EScrollArea(parent=self)
        self.scrollWidget.setWidget(self.mainWidget)

        self.spellWidget = ESpellWidget(parent=self, character=self.mainWidget.currentCharacter)

        self.mainWidget.characterChanged.connect(self.spellWidget.updateCharacter)
        self.mainWidget.spellListsMade.connect(self.spellWidget.createSpellLists)

        self.spell_ScrollWidget = EScrollArea(parent=self)
        self.spell_ScrollWidget.setWidget(self.spellWidget)

        self.tabWidget = QTabWidget()
        self.tabWidget.setStyleSheet("QTabWidget::pane { border: 1px solid lightgray; }")

        self.tabWidget.addTab(self.scrollWidget,"Main Sheet")
        self.tabWidget.addTab(self.spell_ScrollWidget, "Spells")

        self.setCentralWidget(self.tabWidget)

        menuBar = self.menuBar()
        menuFile = menuBar.addMenu('&File')
        menuEdit = menuBar.addMenu('&Edit')

        actionSaveCharacterAs = QAction("&Save Character As", self)
        actionSaveCharacterAs.setShortcut("Ctrl+Shift+S")
        actionSaveCharacterAs.triggered.connect(self.mainWidget.saveCurrentCharacterAs)

        actionSaveCharacter = QAction("&Save Character", self)
        actionSaveCharacter.setShortcut("Ctrl+S")
        actionSaveCharacter.triggered.connect(self.mainWidget.saveCurrentCharacter)

        actionOpenCharacter = QAction("&Open Character", self)
        actionOpenCharacter.setShortcut("Ctrl+O")
        actionOpenCharacter.triggered.connect(self.mainWidget.openCharacter)

        actionRollScores = QAction("&Roll Scores", self)
        actionRollScores.setShortcut("Ctrl+Shift+R")
        actionRollScores.triggered.connect(self.mainWidget.rollScores)

        actionRollDice = QAction("&Roll a Die", self)
        actionRollDice.setShortcut("Ctrl+R")
        actionRollDice.triggered.connect(self.mainWidget.rollDice)

        actionSetOverrides = QAction("Set Score Overrides", self)
        #actionSetOverrides.triggered.connect()

        actionAddFeature = QAction("Add a Feature", self)
        actionAddFeature.triggered.connect(self.mainWidget.addFeature)

        menuFile.addAction(actionSaveCharacterAs)
        menuFile.addAction(actionSaveCharacter)
        menuFile.addAction(actionOpenCharacter)
        menuFile.addAction(actionRollDice)

        menuEdit.addAction(actionRollScores)
        menuEdit.addAction(actionSetOverrides)
        menuEdit.addAction(actionAddFeature)

    def show(self):
        self.scrollWidget.setMinimumWidth(self.mainWidget.size().width()+self.scrollWidget.verticalScrollBar().size().width())
        qApp.processEvents()
        self.scrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        w = qApp.screens()[0].size().width()
        h = qApp.screens()[0].size().height()
        widgetH = self.mainWidget.size().height() + (self.menuBar().sizeHint().height() + 2) + (self.tabWidget.tabBar().size().height()+2)

        if widgetH > h:
            mH = h-(h/4)
        else:
            mH = widgetH

        self.resize(self.size().width(),mH)
        self.move((w-self.size().width())/2,(h-self.size().height())/4)

        self.setVisible(True)

if __name__ == "__main__":
    app = QApplication([])
    MainWindow = Window()
    MainWindow.show()
    sys.exit(app.exec_())
