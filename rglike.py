from typing import Match
import numpy as np
from enum import Enum
import random


items = {"Potion": 25, "Med_Potion": 50, "Super_Potion": 100}
armour = {"Bronze_Helmet": 5, "Silver_Helmet": 10, "Gold_Helmet": 15, "Diamond_Helmet": 25, "Broze_Chestplate": 25,
          "Silver_Chestplate": 50, "Gold_Chestplate": 75, "Diamond_Chestplate": 100,}
weapons = {"Bronze_Sword": 25, "Silver_Sword": 50, "Gold_Sword": 100}
chest = [items, armour, weapons]
inventory = []
equip = {
    'Head': None,
    'Chest': None,
    'Legs': None,
    'Boots': None,
    'Weapon': None
}

class LevelNode:
    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None
        self.parent = None # Add parent attribute

def player_tranverse(node, villager, monster, chest, inventory, equip):
    if node is None:
        print("You've reached a dead end!")
        return

    print(f"\nYou are at node: {node.data}")

    # Randomly determine what's in the room
    room_event = random.choice(["chest", "monster", "empty"])

    if room_event == "chest":
        random_item_category = np.random.choice(chest)
        random_item = np.random.choice(list(random_item_category))

        open_chest = input(f"\nYou found a chest!\n Would you like to open it?: \n")
        if open_chest.lower() == 'y':
            random_item_category = np.random.choice(chest)
            random_item = np.random.choice(list(random_item_category))

            if random_item in items:
                add_to_inventory = input(f"\nYou Pulled a {random_item} from the chest! \nWould you like to add it to your Inventory? (y/n): \n")
                if add_to_inventory.lower() == 'y':
                    inventory.append(random_item)
                    print(f"Your current inventory: {inventory}")
                else:
                    print("\nYou did not add the item to your inventory.\n")
            elif random_item in armour or random_item in weapons: # Check if it's armor or a weapon
                equip_item = input(f"You Pulled a {random_item} from the chest! \n Would you like to Equip it? (y/n): \n")
                if equip_item.lower() == 'y':
                    villager.equipment(random_item)
                    print(f"Your current Equipment: {villager.equip}")
                else:
                    print("You did not equip the item.")

            else:
                print("You found something unidentifiable.")

        else:
            print("You did not open the chest.")

    elif room_event == "monster":
        ran_mon = np.random.choice(monster)
        print(f"\nYou encountered a {ran_mon.name}!\n")
        defeat = False
        while defeat == False:

            # Implement monster encounter/combat logic here
            action = int(input("1.Attack\n2.Defend\n3.Run\n4.Inventory\n"))

            match action:
                case 1:
                    print("\nYou attacked the monster\n")
                    villager.attack(ran_mon)
                    print(f"monster health: {ran_mon.health}")
                    if ran_mon.health <= 0:
                        defeat = True
                        ran_mon.health = 60 # Reset monster health for next encounter

                case 2:
                    print("\nYou defended the monster\n")
                    villager.health += 10
                case 3:
                    print("\nYou ran away from the monster\n")
                    defeat = True
                    break
                case 4:
                    print(f"Your current inventory: {inventory}")
                    pick = int(input("Pick Potion \n 1.potion\n2.Med potion\n3.Super potion\n"))

                    match pick:
                        case 1:
                            if "Potion" in inventory:
                                villager.restore(villager,"Potion")
                                inventory.remove("Potion")
                            else:
                                print("You don't have a Potion.")
                        case 2:
                            if "Med_Potion" in inventory:
                                villager.restore(villager,"Med_Potion")
                                inventory.remove("Med_Potion")
                            else:
                                print("You don't have a Med Potion.")
                        case 3:
                            if "Super_Potion" in inventory:
                                villager.restore(villager,"Super_Potion")
                                inventory.remove("Super_Potion")
                            else:
                                print("You don't have a Super Potion.")

                    print(f"\nYour health {villager.health}\n")

                case _:
                    print("Invalid Input")

            if not defeat: # Only monster attacks if not defeated
                reduction = (villager.protection * .20)
                ran_mon.strength -= reduction

                print(f"\nmonster attacks\n")
                ran_mon.attack(villager)

                print(f"villager health: {villager.health}\n")
                if villager.health <= 0:
                    defeat = True


    else: # empty room
        print("\nYou entered an empty room.")


    # Check if this is a leaf node
    if node.left is None and node.right is None:
        print("This is a leaf node. No further moves except back.")


    choices = []
    if node.left:
        print("L: Go to left child")
        choices.append('L')
    if node.right:
        print("R: Go to right child")
        choices.append('R')
    if node.parent:  # Add option to go back
        print("B: Go back to previous room")
        choices.append('B')


    while True:
        choice = input("Choose your next move (" + "/".join(choices) + "): ").strip().upper()
        if choice == 'L' and 'L' in choices:
            player_tranverse(node.left, villager, monster, chest, inventory, equip)
            break
        elif choice == 'R' and 'R' in choices:
            player_tranverse(node.right, villager, monster, chest, inventory, equip)
            break
        elif choice == 'B' and 'B' in choices: # Handle going back
            player_tranverse(node.parent, villager, monster, chest, inventory, equip)
            break
        else:
           print("Invalid choice. Try again")


class GameMenu():
  def __init__(self):
    self.option = None
    self.menu = None
    self.quit_game = False
    self.create_menu() # Call create_menu here

  def create_menu(self):
    self.menu = {"Start Game:": self.start_game, "Quit Game": self.quit_game}
    UP = "W"
    DOWN = "S"
    LEFT = "A"
    RIGHT = "D"

  def start_game(self): # Define a placeholder start_game method
      print("Starting the game...")


class Rooms():
  def __init__(self):
    self.direction = ["Right room", "Left room", "Front room", "Go Back"]

  def randum_room(self):
    rand_room = []
    available_directions = self.direction[:] # Create a copy of the direction list
    randum_gen = np.random.randint(1, len(available_directions) + 1) # Ensure randum_gen is within bounds
    while len(rand_room) < randum_gen and available_directions: # Add check for available_directions
      chosen_direction = np.random.choice(available_directions)
      rand_room.append(chosen_direction)
      available_directions.remove(chosen_direction) # Remove chosen direction from the copy
    return rand_room



class Monsters():
  def __init__(self,name,health,strength):
    self.name = name
    self.health = health
    self.strength = strength

  def attack(self, other):
    other.health -= self.strength
    print(f"{self.name} attacks {other.name} for {self.strength} damage. ")
    print(f"{other.name} has {other.health} health remaining.")
    if other.health <= 0:
      print(f"{other.name} has been defeated!")
      return True
    else:
      return False

class Hero():
    equip = { "Head": None,
              "Chest": None,
              "Legs": None,
              "Boots": None,
              "Hands": None
            }

    def __init__(self,name,health,strength,protection):

        self.name = name
        self.health = health
        self.strength = strength
        self.protection = protection
        self.base_protection = protection # Store base protection


    def __str__(self):
        return f"{self.name} has {self.health} health and {self.strength} strength."

    #move equipment function here to call on object
    def equipment(self, rand_item):
        if "Helmet" in rand_item:
            if self.equip['Head'] is not None:
                self.protection -= armour[self.equip['Head']] # Subtract old item stats
            self.equip['Head'] = rand_item
            self.protection += armour[rand_item] # Add new item stats


        elif "Chestplate" in rand_item:
            if self.equip['Chest'] is not None:
                self.protection -= armour[self.equip['Chest']] # Subtract old item stats
            self.equip['Chest'] = rand_item
            self.protection += armour[rand_item] # Add new item stats


        elif "Leg" in rand_item:
            if self.equip['Legs'] is not None:
                self.protection -= armour[self.equip['Legs']] # Subtract old item stats
            self.equip['Legs'] = rand_item
            self.protection += armour[rand_item] # Add new item stats


        elif rand_item in weapons:
            if self.equip['Hands'] is not None:
                self.strength -= weapons[self.equip['Hands']] # Subtract old item stats
            self.equip['Hands'] = rand_item
            self.strength += weapons[rand_item] # Add new item stats


    def attack(self, other):
        other.health -= self.strength
        print(f"{self.name} attacks {other.name} for {self.strength} damage. ")
        print(f"{other.name} has {other.health} health remaining.")
        if other.health <= 0:
            print(f"{other.name} has been defeated!")
            return True
        else:
            return False

    def restore(self,other,potion):
        self.health += items.get(potion)
        print(f"{self.name} has restored {items.get(potion)} health.")
        print(f"{self.name} has {self.health} health remaining.")

villager = Hero("Bob", 100, 5, 0)
troll = Monsters("Troll", 100, 20)
goblin = Monsters("goblin", 60,15)

monster = [troll, goblin]


Menu = GameMenu()
room_gen = Rooms() # Create an instance of the Rooms class



while Menu.quit_game == False:
  print("Welcome to the game!")
  print("Please select an option:")
  print("1. Start Game")
  print("2. Quit Game")

  choice = input("Enter your choice: ")

  match choice:
    case "1":
      Menu.start_game()

      # Create a simple tree structure for levels
      root = LevelNode("Starting Room")
      node1 = LevelNode("Left Room")
      node2 = LevelNode("Right Room")
      node3 = LevelNode("Deep Left Room")
      node4 = LevelNode("Shallow Left Room")
      node5 = LevelNode("Deep Right Room")
      node6 = LevelNode("Shallow Right Room")

      # Set parent nodes
      node1.parent = root
      node2.parent = root
      node3.parent = node1
      node4.parent = node1
      node5.parent = node2
      node6.parent = node2

      root.left = node1
      root.right = node2

      node1.left = node3
      node1.right = node4

      node2.left = node5
      node2.right = node6

      # Start traversing the tree
      player_tranverse(root, villager, monster, chest, inventory, equip)


    case "2":
      Menu.quit_game = True
    case _:
      print("Invalid choice. Please try again.")

print("Thank you for using the game!")
