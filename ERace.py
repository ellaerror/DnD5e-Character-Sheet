class ERace():
    def __init__(self, name, parent=None):
        if not parent:
            self.parent = name
        else:
            self.parent = parent
        self.name = name
        self.alignment = "Often Neutral"
        self.languages = ["Common"]
        self.matureAge = 18
        self.oldAge = 80
        self.features = []
        self.speed = 30
        self.size = "M"
        self.proficiencies = {'Armor':[],'Weapon':[],'Tool':[],'Skill':[]}
        self.scoreMods = [0,0,0,0,0,0]

    def getModString(self,num):
        if self.scoreMods[num] >= 0:
            return "+"+str(self.scoreMods[num])
        else:
            return str(self.scoreMods[num])

    def toLine(self):
        string = ""
        string += self.parent+","
        string += self.name+","
        string += str(self.speed)+","
        string += self.size+","
        string += str(self.matureAge)+","
        string += str(self.oldAge)+","
        string += ";".join(self.languages)+","
        string += self.alignment.replace(",","$")+","
        for num in self.scoreMods:
            string += str(num)+","
        fList = []
        for feat in self.features:
            fList.append(":".join(feat).replace("\n","<>").replace(",","$"))
        string += ";".join(fList)+","
        string += ";".join(self.proficiencies['Armor'])+","
        string += ";".join(self.proficiencies['Tool'])+","
        string += ";".join(self.proficiencies['Weapon'])+","
        string += ";".join(self.proficiencies['Skill'])
        return string

    def fromLine(linedata):
        data = linedata.strip().split(",")
        temp = ERace(data[1],data[0])
        temp.speed = int(data[2])
        temp.size = data[3]
        temp.matureAge = int(data[4])
        temp.oldAge = int(data[5])
        temp.languages = data[6].split(";")
        temp.alignment = data[7].replace("$",",")
        temp.scoreMods = [int(data[8]),int(data[9]),int(data[10]),int(data[11]),int(data[12]),int(data[13])]
        fList = data[14].split(";")
        for f in fList:
            temp.features.append(f.replace("<>","\n").replace("$",",").split(":"))
        temp.proficiencies['Armor'] = data[15].split(";")
        temp.proficiencies['Weapon'] = data[16].split(";")
        temp.proficiencies['Tool'] = data[17].split(";")
        temp.proficiencies['Skill'] = data[18].split(";")
        return temp

def importRaces(path):
    races = []
    file = open(path,"r")
    line = file.readline()
    while line:
        data = line.strip().split(",")
        temp = ERace(data[1],data[0])
        temp.speed = int(data[2])
        temp.size = data[3]
        temp.matureAge = int(data[4])
        temp.oldAge = int(data[5])
        temp.languages = data[6].split(";")
        temp.alignment = data[7].replace("$",",")
        temp.scoreMods = [int(data[8]),int(data[9]),int(data[10]),int(data[11]),int(data[12]),int(data[13])]
        fList = data[14].split(";")
        for f in fList:
            temp.features.append(f.replace("<>","\n").replace("$",",").split(":"))
        temp.proficiencies['Armor'] = data[15].split(";")
        temp.proficiencies['Weapon'] = data[16].split(";")
        temp.proficiencies['Tool'] = data[17].split(";")
        temp.proficiencies['Skill'] = data[18].split(";")
        races.append(temp)
        line = file.readline()
    return races
