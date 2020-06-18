import math, copy

class ECharacter():
    def __init__(self, race, mainclass, subclass, background, level=1, name="Character Name", abilityScores=[10,10,10,10,10,10]):
        self.subrace = race
        self.parentrace = race.parent
        self.mainclass = mainclass
        self.subclass = subclass
        self.background = background
        self.level = level
        self.exp = 0
        self.name = name
        self.pb = math.floor(((self.level-1)/4)+2)
        self.druidLand = None
        self.spells = []
        self.pactBoon = None

        self.armorClass = None
        self.initiative = None

        self.baseAbilityScores = copy.deepcopy(abilityScores)
        self.abilityScores = copy.deepcopy(abilityScores)
        self.updateAbilityScores()

        self.maxHp = self.mainclass.hitDie + (math.ceil(self.mainclass.hitDie/2)*(self.level-1))
        self.currentHp = self.maxHp

        self.speed = race.speed

        self.traits = ""
        self.ideals = ""
        self.bonds = ""
        self.flaws = ""

    def setName(self, name):
        self.name = name

    def setArmorClass(self, num):
        self.armorClass = num

    def setSpeed(self, num):
        self.speed = num

    def setInitiative(self, num):
        self.initiative = num

    def getMod(self, num):
        return math.floor((self.abilityScores[num]-10)/2)

    def getModString(self, num, add=0, mul=1):
        if (self.getMod(num)+add) >= 0:
            return "+"+str((self.getMod(num)+add)*mul)
        else:
            return str((self.getMod(num)+add)*mul)

    def updateAbilityScores(self):
        for num in range(len(self.abilityScores)):
            self.abilityScores[num] = self.baseAbilityScores[num]+self.subrace.scoreMods[num]

    def setDruidLand(self, land):
        self.druidLand = land

    def setLevel(self, num):
        self.level = num
        self.pb = math.floor(((self.level-1)/4)+2)

    def setExp(self, num):
        self.exp = num

    def setMaxHp(self, num):
        self.maxHp = num

    def setCurHp(self, num):
        self.currentHp = num

    def setTraits(self, text):
        self.traits = text.replace("\n","<br>").replace(",","$")

    def setIdeals(self, text):
        self.ideals = text.replace("\n","<br>").replace(",","$")

    def setBonds(self, text):
        self.bonds = text.replace("\n","<br>").replace(",","$")

    def setFlaws(self, text):
        self.flaws = text.replace("\n","<br>").replace(",","$")

    def getTraits(self):
        return self.traits.replace("<br>","\n").replace("$",",")

    def getIdeals(self):
        return self.ideals.replace("<br>","\n").replace("$",",")

    def getBonds(self):
        return self.bonds.replace("<br>","\n").replace("$",",")

    def getFlaws(self):
        return self.flaws.replace("<br>","\n").replace("$",",")

    def getPBString(self):
        return "+"+str(self.pb)

    def toLine(self):
        string = ""
        string += self.name+"," #0
        string += str(self.level)+","+str(self.exp)+"," #1, 2
        string += str(self.maxHp)+","+str(self.currentHp)+"," #3, 4
        string += ",".join(str(x) for x in self.baseAbilityScores) #5,6,7,8,9,10
        string += ","+self.traits+","+self.ideals+","+self.bonds+","+self.flaws #11,12,13,14
        string += ","+str(self.armorClass)+","+str(self.initiative)+","+str(self.speed) #15,16,17
        return string
