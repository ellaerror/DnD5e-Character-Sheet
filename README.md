# DnD5e-Character-Sheet

A DnD 5e character sheet with options for subclasses, spells, and more.

## Prerequisites

- PyQt 5.15 or higher `pip install PyQt5`
- [Python 3.7 or higher](https://www.python.org/downloads/)

*When installing Python, ensure that it's properly added to your path environment variable!*

## How to Run

- Double-click the python file called "character-sheet.pyw" to run the program. (This hides the command shell)
-  Or you can run the command `py character-sheet.pyw` in a cmdline shell or powershell console.

## Using the Program

### The Main Sheet

#### Class, Subclass, Background, Race, Level, and EXP

Choose your class, subclass, background, race, and subrace by selecting options from the dropdown menus at the top of the "Main Sheet" tab. Selecting these options will change your features and traits, as well as your skills and inventory in some cases. 

You can change your level and EXP in the boxes at the top of the sheet as well, although the level box is the only one that actually affects the rest of the sheet. 

#### Ability Scores

Roll your character's ability scores by pressing Ctrl+Shift+R, or pressing Edit>Roll Scores. In the resulting pop-up window, you can choose the options for how you want to roll your ability scores. You can choose what dice to roll, such as 3d6, 4d6, 2d6+6, or even 5d4. Make sure to check with your Dungeon Master before using this roll feature and make sure they approve of the methods used. 

When you press the "Roll" button, 6 ability scores will show up in the boxes below it. You can then drag and drop these ability scores into the ability score boxes on the right. To finalize your selection, press the "Use" button at the bottom. This will import your scores into the main program. Pressing "Cancel" won't affect anything in the main program. 

If you wish to use scores that you rolled outside the program, simply enter the scores in the left-most small box in the ability score section. Your racial modifier will be shown in the center box, and the resulting score shown in the right-most box. 

#### Proficiencies and Skills

To change your proficiency in a saving throw or skill, simply check or uncheck the box next to it. The program will automatically calculate your modifier. If you have proficiency in a skill, you can also add expertise to it by checking the box to the left of the main proficiency box. 

When you change your class, race, or background, your proficiencies will automatically be updated in the proficiencies and languages box. You can add custom proficiencies by pressing the "+" button in the bottom right, or remove proficiencies by pressing the "-" button in the bottom left. You can also edit any proficiency by double clicking the part you'd like to edit. 

Proficiencies and skills are tracked by their source, such as your class or race. So if you change your class, some of your proficiencies will change. User-added proficiencies are added with a "Custom" source, so they will not be removed when you change any character options. Even if you edit a proficiency, the source does not change. So for example, if you have a proficiency for a language from your class that's "Choose any language" and you change it to be "Dwarvish", if you change your class, that proficiency will disappear. 

The source of your proficiencies is not shown on the list to preserve readability on smaller screens.

#### Armor Class

Your armor class is calculated automatically as if you were not wearing armor, so it equals 10+your DEX mod. If you're a monk or a barbarian, it also automatically adds your Unarmored Defense bonus. 

If you have armor or your have natural armor from your race, you can change this number manually. However, once you change it it will no longer be updated automatically and you'll need to update it on your own.

#### Initiative

Your initiative bonus is equal to your dexterity modifier. If you have a feat or trait that gives you an additional bonus, you can change this number manually. However, if you change it manually, it will no longer update if your dexterity modifer changes. 

#### Speed

Your speed is calculated based off of your race. If you're a monk or a barbarian, this program accounts for your Unarmored Movement. However, if you have items or features that add to this number you can change it manually. 

Your speed is updated when you change your class, race, or level. This will override any manual changes to your speed. 

#### Hit Points and Hit Dice

Your hit point maximum is calculated based off of your classes hit die and your constitution modifier as if you were a level one character. If you're creating a higher level character or you're leveling up, you can change this manually and it will not be updated unless you change your class. 

Your hit dice box simply says your hit dice total and how many you have left. Your hit dice replenish on a long rest, and you can use them on a short rest to restore hit points. The number box contains the amount of hit dice you have left for the day, and you can edit this to be lower when you use your hit dice. 

If you'd like to roll your hit dice in the program, see the section on rolling dice. 

#### Death Saves

The death saves section here allows you to check and un-check death saves for your character. It does not affect the rest of the sheet mechanically.

#### Attacks and Spells

In this box you can add attacks and spells for your weapons and spells. To add or remove items, use the "-" and "+" buttons at the bottom. Double-click to edit the items. 

#### Equipment

You can edit any of the boxes for currency to change how much currency your character has. 

To add or remove items from your inventory, use the "-" or "+" buttons below the currency and to the left of the inventory. In the inventory, items have a name and a weight. The weight may be used by some DMs to keep track of encumberence. 

Your equipment is automatically compiled based on your class and background. Equipment is tracked by its source, such as your class or background. So if you change your class, some of your equipment will change. User-added equipment is added with a "Custom" source, so it will not be removed when you change any character options. Even if you edit an item, the source does not change. So for example, if you have an item from your class called "chain mail or leather armor" and you change it to say "chain mail", it would still be removed if your change your class.

#### Personality Traits

The personality traits boxes are there for you to fill out your character's personality, ideals, bonds, and flaws. They have no effect on anything else on the sheet.

#### Features and Traits

The features and traits box shows all the features and traits your character has. It shows the name of the trait in bold, followed by the source of the trait and the level it was earned at (if applicable). If you click on the feature, it will show a detailed description of it. 

These descriptions were manually copied by me from wikis and source books and are not guarenteed to be 100% accurate. Additionally, they might contain formatting errors or spacing issues. If you see any errors, please message me or open an issue with the trait and the source, and a screen shot of the issue. 

You can add your own features and traits by pressing Edit>Add a Feature. This is so you can add feats or custom traits if you'd like. Unfortunately the program doesn't have the ability to remove traits at this time. 

### Spells

If your class has the ability to cast spells, you can select them using the Spells tab. 

#### Spellcasting ability, modifiers, etc.

Your spellcasting class and ability score are displayed in the top left corner of the page. In addition, the sheet calculates your Spell Save DC and your spell attack bonus. If your class can only know a limited amount of spells, the amount is displayed in the Spells Known box, otherwise it will read "N/A". If your class has to prepare spells, the amount they can prepare is displayed in the preparable spells box. It's important to note that even if your class does not have to prepare spells, a number will be displayed here. In this case, you can ignore it. It does not have an effect on the program.

If you're a sorcerer, then your sorcery points will be displayed in the top right as well once you reach level 2. 

#### Spells

Spells are organized by their level. To add a spell, just press the "+" button on in the correlating level box. The spells that are available for you to add are filtered based on your class, subclass, and in some cases your race. Unfortunately, the spell list provided in this program is not exhaustive in detailing subclass and race specific spells, so those may not appear for you, even if your features say you can learn them. If you find this is the case, please contact me or raise an issue.

In your spell list, spells show a few basic features about them. From left to right, each spell shows a checkbox to show if it's prepared or not, its name, if it's a ritual or a concentration spell, the casting time, and the components of the spell. If you'd like to see more details about a spell, click it once to see the description. If you want to see the whole spell card, double-click the spell name or description. This will open a popup window with the spell card on it. You can have as many spell cards open as you want. 

Warlocks and Artificers will see their Invocation/Infusion list appear below the 6th level spell list when those options become available to them. 

### Rolling Dice

To open the dice roll prompt, press Crtl+R, or press File>Roll a Die.

Here, you can choose how many dice to roll, what kind of die, and to add any modifier. You can add a negative modifier as well. To roll, just press the roll button. The prompt will display all of the induvidual rolls made and the modifier added. The final score is displayed in the while box.
