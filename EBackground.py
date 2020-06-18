class EBackground():
    def __init__(self,name):
        self.name = name
        self.gp = 0
        self.addLang = 0
        self.proficiencies = {'Tool':[],'Skill':[]}
        self.features = []
        self.startingEquipment = []

    def toLine(self):
        string = ""
        string += self.name+","
        string += str(self.addLang)+","
        string += ";".join(self.proficiencies['Tool'])+","
        string += ",".join(self.proficiencies['Skill'])+","
        string += ";".join(":".join(x) for x in self.features).replace(",","$").replace("\n","<>")+","
        string += str(self.gp)+","
        string += ";".join(self.startingEquipment)
        return string

    def fromLine(linedata):
        data = linedata.strip().split(",")
        # Name
        temp = EBackground(data[0])
        # Add. Languages
        temp.addLang = int(data[1])
        # Proficiencies
        temp.proficiencies['Tool'] = data[2].replace("$",",").split(";")
        temp.proficiencies['Skill']= [data[3]]
        temp.proficiencies['Skill'].append(data[4])
        # Features
        temp.features = data[5].replace("<>","\n").replace("$",",").split(";")

        for i in range(0,len(temp.features)):
            temp.features[i] = temp.features[i].split(":")
        # GP
        temp.gp = int(data[6])
        # Equipment
        temp.startingEquipment = data[7].split(";")
        return temp

def importBackgrounds(path):
    file = open(path,"r")
    backgrounds = []
    data = file.readline().strip().split(",")
    while data:
        if len(data) < 2:
            break
        # Name
        temp = EBackground(data[0])
        # Add. Languages
        temp.addLang = int(data[1])
        # Proficiencies
        temp.proficiencies['Tool'] = data[2].split(";")
        temp.proficiencies['Skill']= [data[3]]
        temp.proficiencies['Skill'].append(data[4])
        # Features
        temp.features = data[5].replace("<>","\n").replace("$",",").split(";")

        for i in range(0,len(temp.features)):
            temp.features[i] = temp.features[i].split(":")
        # GP
        temp.gp = int(data[6])
        # Equipment
        temp.startingEquipment = data[7].split(";")

        backgrounds.append(temp)

        data = file.readline().strip().split(",")
    return backgrounds
