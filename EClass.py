class EClass():
    def __init__(self, name="Class Name"):
        self.name = name
        self.features = [
            [],
            [],
            [],
            [["Ability Score Improvement","You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can’t increase an ability score above 20 using this feature.\nUsing the optional feats rule, you can forgo taking this feature to take a feat of your choice instead."]],
            [],
            [],
            [],
            [["Ability Score Improvement","You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can’t increase an ability score above 20 using this feature.\nUsing the optional feats rule, you can forgo taking this feature to take a feat of your choice instead."]],
            [],
            [],
            [],
            [["Ability Score Improvement","You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can’t increase an ability score above 20 using this feature.\nUsing the optional feats rule, you can forgo taking this feature to take a feat of your choice instead."]],
            [],
            [],
            [],
            [["Ability Score Improvement","You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can’t increase an ability score above 20 using this feature.\nUsing the optional feats rule, you can forgo taking this feature to take a feat of your choice instead."]],
            [],
            [],
            [["Ability Score Improvement","You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can’t increase an ability score above 20 using this feature.\nUsing the optional feats rule, you can forgo taking this feature to take a feat of your choice instead."]],
            []
        ]
        self.subclasses = []
        self.hitDie = 6
        self.savingThrows = ["",""]
        self.proficiencies = {'Armor':[],'Weapon':[],'Tool':[],'Skill':[]}
        self.startingEquipment = []
        self.spellcastingAbility = ""

        self.spellcasting = False
        self.spellsKnown = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # COLUMN IS SPELL LEVEL
        # ROW IS CLASS LEVEL
        self.spellSlots = [
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0]
        ]
        # Examples: ki, rages, sorcery points, etc.
        self.altClassResource = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.altClassResourceName = ""

    def toLine(self):
        data = ""
        data += self.name+","
        data += str(self.hitDie)+","
        for feat in self.features:
            data += ";".join(":".join(x) for x in feat).replace("\n","<>").replace(",","$").replace(";","`")+","
        data+= self.spellcastingAbility+","+",".join(self.savingThrows)+","
        for k,p in self.proficiencies.items():
            if k != 'Skill':
                data += ";".join(p)+","
            else:
                if len(p)>1:
                    data += p[0]+";"+"|".join(p[1])+","
                else:
                    data += ";".join(p)+","
        elist = []
        for e in self.startingEquipment:
            elist.append("|".join(e))
        data += ";".join(elist)+","
        for i in range(0,20):
            data += self.spellsKnown[i]+","+",".join(self.spellSlots[i])+","
        data = data[:-1]
        return data

    def fromLine(linedata):
        data = linedata.strip().split(",")
        # Name
        temp = EClass(data[0])
        # Hit Die
        temp.hitDie = int(data[1])
        # Features
        for i in range(2,22):
            temp.features[i-2] = data[i].replace("<>","\n").replace("$",",").split(";")
        for i in range(0,len(temp.features)):
            for j in range(0,len(temp.features[i])):
                temp.features[i][j] = temp.features[i][j].split(":")
        # Spellcasting Ability
        temp.spellcastingAbility = data[22]
        if data[22] != "None":
            temp.spellcasting = True
        # Saving Throws
        temp.savingThrows = [data[23],data[24]]
        # Proficiencies
        temp.proficiencies['Armor']   = data[25].split(";")
        temp.proficiencies['Weapon'] = data[26].split(";")
        temp.proficiencies['Tool']   = data[27].split(";")
        temp.proficiencies['Skill']  = data[28].split(";")
        try:
            temp.proficiencies['Skill'][1] = temp.proficiencies['Skill'][1].split("|")
        except:
            pass
            #print(data[28])
        # Equipment
        elist = data[29].split(";")
        for t in elist:
            temp.startingEquipment.append(t.split("|"))
        # Spell Slots
        for i in range(0, 20):
            temp.spellsKnown[i] = data[30+(i*11)]
            lvlList = []
            for j in range(1, 11):
                lvlList.append(data[30+(i*11)+j])
            temp.spellSlots[i] = lvlList
        return temp

class ESubclass():
    def __init__(self, name="Subclass Name"):
        self.name = name
        self.parent = name
        self.basename=name
        self.features = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

        self.proficiencies = {'Armor':[],'Weapon':[],'Tool':[],'Skill':[]}
        self.startingEquipment = []

        self.spellcastingAbility = None

        self.spellcasting = None
        self.spellsKnown = None
        self.spellSlots = None
        # Examples: ki, rages, sorcery points, etc.
        self.altClassResource = None
        self.altClassResourceName = None

    def toLine(self):
        string = ""
        string += self.parent+","
        string += self.name+","
        string += self.basename+","
        fList = []
        for level in self.features:
            fList.append(";".join(":".join(x) for x in level).replace(",","$").replace("\n","<>").replace(";","`"))
        string += ",".join(fList)+","
        if self.spellcasting:
            string += "1,"
            for i in range(0,20):
                string += self.spellsKnown[i]+","+",".join(self.spellSlots[i])+","
            string = string[:-1]
        else:
            string += "0"
        return string

    def fromLine(linedata):
        data = linedata.strip().split(",")
        temp = ESubclass(data[1])
        temp.parent = data[0]
        for i in range(2,22):
            temp.features[i-2] = data[i].replace("<>","\n").replace("$",",").split(";")

        for i in range(0,len(temp.features)):
            for j in range(0,len(temp.features[i])):
                temp.features[i][j] = temp.features[i][j].split(":")
                temp.features[i][j][-1] = temp.features[i][j][-1].replace("~",":")

        if data[23] == "1":
            temp.spellcasting = True
        else:
            temp.spellcasting = False

        if temp.spellcasting:
            temp.spellcastingAbility = data[24]
            temp.spellsKnown = [0 for x in range(0,20)]
            # COLUMN IS SPELL LEVEL
            # ROW IS CLASS LEVEL
            temp.spellSlots = [[0 for x in range(0,10)] for x in range(0,20)]
            for i in range(0, 20):
                temp.spellsKnown[i] = data[25+(i*11)]
                lvlList = []
                for j in range(1, 11):
                    lvlList.append(data[25+(i*11)+j])
                temp.spellSlots[i] = lvlList

        return temp

def importSubclasses(path,classes):
    file = open(path, "r")
    subclasses = []
    # GET RID OF THE HEADER
    data = file.readline()
    data = file.readline().strip().split(",")
    while data:
        if len(data) < 2:
            break
        # Gather the class data
        temp = ESubclass(data[1])
        temp.basename=data[2]
        temp.parent = data[0]
        for i in range(3,23):
            temp.features[i-3] = data[i].replace("<>","\n").replace("$",",").split(";")

        for i in range(0,len(temp.features)):
            for j in range(0,len(temp.features[i])):
                temp.features[i][j] = temp.features[i][j].split(":")
                temp.features[i][j][-1] = temp.features[i][j][-1].replace("~",":").replace("`",";")

        if data[23] == "1":
            temp.spellcasting = True
        else:
            temp.spellcasting = False

        if temp.spellcasting:
            temp.spellcastingAbility = data[24]
            temp.spellsKnown = [0 for x in range(0,20)]
            # COLUMN IS SPELL LEVEL
            # ROW IS CLASS LEVEL
            temp.spellSlots = [[0 for x in range(0,10)] for x in range(0,20)]
            for i in range(0, 20):
                temp.spellsKnown[i] = data[25+(i*11)]
                lvlList = []
                for j in range(1, 11):
                    lvlList.append(data[25+(i*11)+j])
                temp.spellSlots[i] = lvlList

        # Append it to the class list
        for c in classes:
            if c.name == data[0]:
                c.subclasses.append(temp)

        data = file.readline().strip().split(",")

def importClasses(path):
    file = open(path,"r")
    classes = []
    data = file.readline().strip().split(",")
    while data:
        # Name
        temp = EClass(data[0])
        # Hit Die
        temp.hitDie = int(data[1])
        # Features
        for i in range(2,22):
            temp.features[i-2] = data[i].replace("<>","\n").replace("$",",").split(";")
        for i in range(0,len(temp.features)):
            for j in range(0,len(temp.features[i])):
                temp.features[i][j] = temp.features[i][j].split(":")
                temp.features[i][j][-1] = temp.features[i][j][-1].replace("~",":").replace("`",";")
        # Spellcasting Ability
        temp.spellcastingAbility = data[22]
        if data[22] != "None":
            temp.spellcasting = True
        # Saving Throws
        temp.savingThrows = [data[23],data[24]]
        # Proficiencies
        temp.proficiencies['Armor']   = data[25].split(";")
        temp.proficiencies['Weapon'] = data[26].split(";")
        temp.proficiencies['Tool']   = data[27].split(";")
        temp.proficiencies['Skill']  = data[28].split(";")
        # Equipment
        elist = data[29].split(";")
        for t in elist:
            temp.startingEquipment.append(t.split("|"))
        # Spell Slots
        for i in range(0, 20):
            temp.spellsKnown[i] = data[30+(i*11)]
            lvlList = []
            for j in range(1, 11):
                lvlList.append(data[30+(i*11)+j])
            temp.spellSlots[i] = lvlList

        classes.append(temp)
        data = file.readline().strip().split(",")
        if len(data) < 2:
            break
    file.close()
    return classes

def writeClasses(path,classes):
    file = open(path,"w")
    for c in classes:
        data = ""
        data += c.name+","
        data += str(c.hitDie)+","
        for feat in c.features:
            data += ";".join(feat)+","
        data+= c.spellcastingAbility+","+",".join(c.savingThrows)+","
        for k,p in c.proficiencies.items():
            if k != 'Skill':
                data += ";".join(p)+","
            else:
                data += p[0]+";"+"|".join(p[1])+","
        elist = []
        for e in c.startingEquipment:
            elist.append("|".join(e))
        data += ";".join(elist)+","
        for i in range(0,20):
            data += c.spellsKnown[i]+","+",".join(c.spellSlots[i])+","
        data = data[:-1]
        data += "\n"
        file.write(data)
    file.close()
