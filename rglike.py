import pygame
import sys
import random
import numpy as np
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# Game data
items = {"Potion": 25, "Med_Potion": 50, "Super_Potion": 100}
armour = {
    "Bronze_Helmet": 5, "Silver_Helmet": 10, "Gold_Helmet": 15, "Diamond_Helmet": 25,
    "Bronze_Chestplate": 25, "Silver_Chestplate": 50, "Gold_Chestplate": 75, 
    "Diamond_Chestplate": 100, "Mithril_Chestplate": 125,
    "Bronze_Legs": 10, "Silver_Legs": 15, "Gold_Legs": 20, "Diamond_Legs": 25, "Mithril_Legs": 30,
    "Bronze_Boots": 2, "Silver_Boots": 4, "Gold_Boots": 8, "Diamond_Boots": 16, "Mithril_Boots": 24,
}
weapons = {
    "Bronze_Sword": 25, "Silver_Sword": 30, "Gold_Sword": 40, "Diamond_Sword": 50, "Mithril_Sword": 70,
    "Bronze_Spear": 30, "Silver_Spear": 35, "Gold_Spear": 45, "Diamond_Spear": 55, "Mithril_Spear": 75,
    "Bronze_Dagger": 10, "Silver_Dagger": 15, "Gold_Dagger": 25, "Diamond_Dagger": 30, "Mithril_Dagger": 40,
    "Light_Bow": 20, "Compact_Bow": 40, "Heavy_Bow": 60, "Mithril_Bow": 72
}

chest = [items, armour, weapons]

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    COMBAT = 3
    INVENTORY = 4
    CHEST = 5
    GAME_OVER = 6
    VICTORY = 7

class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.hover_color = LIGHT_GRAY
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class LevelNode:
    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None
        self.parent = None
        self.visited = False

class Hero:
    def __init__(self, name, health, strength, protection):
        self.name = name
        self.max_health = health
        self.health = health
        self.strength = strength
        self.base_strength = strength
        self.protection = protection
        self.base_protection = protection
        self.equip = {
            "Head": None, "Chest": None, "Legs": None, 
            "Boots": None, "Hands": None
        }
        self.inventory = []

    def equipment(self, item):
        if "Helmet" in item:
            if self.equip['Head'] is not None:
                self.protection -= armour[self.equip['Head']]
            self.equip['Head'] = item
            self.protection += armour[item]
        elif "Chestplate" in item:
            if self.equip['Chest'] is not None:
                self.protection -= armour[self.equip['Chest']]
            self.equip['Chest'] = item
            self.protection += armour[item]
        elif "Legs" in item:
            if self.equip['Legs'] is not None:
                self.protection -= armour[self.equip['Legs']]
            self.equip['Legs'] = item
            self.protection += armour[item]
        elif "Boots" in item:
            if self.equip['Boots'] is not None:
                self.protection -= armour[self.equip['Boots']]
            self.equip['Boots'] = item
            self.protection += armour[item]
        elif item in weapons:
            if self.equip['Hands'] is not None:
                self.strength -= weapons[self.equip['Hands']]
            self.equip['Hands'] = item
            self.strength += weapons[item]

    def attack(self, other):
        damage = max(1, self.strength * 0.6 - (other.protection * 0.1))  # Reduced damage multiplier
        other.health -= damage
        return damage

    def use_potion(self, potion):
        if potion in self.inventory:
            heal_amount = items[potion]
            self.health = min(self.max_health, self.health + heal_amount)
            self.inventory.remove(potion)
            return heal_amount
        return 0

class Monster:
    def __init__(self, name, health, strength, protection=0):
        self.name = name
        self.max_health = health
        self.health = health
        self.strength = strength
        self.protection = protection

    def attack(self, other):
        damage = max(1, self.strength - (other.protection * 0.2))
        other.health -= damage
        return damage

    def reset_health(self):
        self.health = self.max_health

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.hero = Hero("Bob", 100, 50, 0)
        self.current_node = None
        self.current_monster = None
        self.current_chest_item = None
        self.current_chest_category = None
        self.boss_defeated = False
        
        self.setup_tree()
        self.create_monsters()
        
        # UI Elements
        self.message = ""
        self.message_timer = 0

    def setup_tree(self):
        # Create the tree structure
        self.root = LevelNode("Starting Room")
        node1 = LevelNode("Left Room")
        node2 = LevelNode("Right Room")
        node3 = LevelNode("Deep Left Room")
        node4 = LevelNode("Shallow Left Room")
        node5 = LevelNode("Deep Right Room")
        node6 = LevelNode("Shallow Right Room")
        node7 = LevelNode("Deep Underground-Left Left")
        node8 = LevelNode("Deep Underground-Left Right")
        node9 = LevelNode("Deep Underground Middle-Left Left")
        node10 = LevelNode("Deep Underground Middle-Left Right")
        node11 = LevelNode("Deep Underground Middle-Right Left")
        node12 = LevelNode("Deep Underground Middle-Right Right")
        node13 = LevelNode("Deep Underground-Right Left")
        node14 = LevelNode("Deep Underground-Right Right")

        # Set relationships
        self.root.left = node1
        self.root.right = node2
        
        node1.parent = self.root
        node2.parent = self.root
        
        node1.left = node3
        node1.right = node4
        node2.left = node5
        node2.right = node6
        
        node3.parent = node1
        node4.parent = node1
        node5.parent = node2
        node6.parent = node2
        
        node3.left = node7
        node3.right = node8
        node4.left = node9
        node4.right = node10
        node5.left = node11
        node5.right = node12
        node6.left = node13
        node6.right = node14
        
        node7.parent = node3
        node8.parent = node3
        node9.parent = node4
        node10.parent = node4
        node11.parent = node5
        node12.parent = node5
        node13.parent = node6
        node14.parent = node6

        # Find leaf nodes and set boss room
        leaf_nodes = []
        self.find_leaf_nodes(self.root, leaf_nodes)
        boss_room_node = random.choice(leaf_nodes)
        boss_room_node.data = "Boss Room"
        
        self.current_node = self.root

    def find_leaf_nodes(self, node, leaf_nodes):
        if node is None:
            return
        if node.left is None and node.right is None:
            leaf_nodes.append(node)
        else:
            self.find_leaf_nodes(node.left, leaf_nodes)
            self.find_leaf_nodes(node.right, leaf_nodes)

    def create_monsters(self):
        self.monsters = [
            Monster("Troll", 100, 20),
            Monster("Goblin", 60, 15),
            Monster("Orc", 80, 18),
            Monster("Skeleton", 50, 12)
        ]

    def show_message(self, message, duration=3000):
        self.message = message
        self.message_timer = duration

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("RPG ADVENTURE", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        start_button = Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "Start Game", GREEN)
        quit_button = Button(SCREEN_WIDTH//2 - 100, 380, 200, 50, "Quit Game", RED)
        
        start_button.draw(self.screen)
        quit_button.draw(self.screen)
        
        return start_button, quit_button

    def draw_game(self):
        self.screen.fill(DARK_GRAY)
        
        # Draw room info
        room_text = self.font.render(f"Current Room: {self.current_node.data}", True, WHITE)
        self.screen.blit(room_text, (20, 20))
        
        # Draw hero stats
        self.draw_hero_stats()
        
        # Draw movement buttons
        buttons = []
        y_start = 400
        
        if self.current_node.left:
            left_btn = Button(50, y_start, 150, 40, "Go Left", BLUE, WHITE)
            buttons.append(("left", left_btn))
            left_btn.draw(self.screen)
        
        if self.current_node.right:
            right_btn = Button(220, y_start, 150, 40, "Go Right", BLUE, WHITE)
            buttons.append(("right", right_btn))
            right_btn.draw(self.screen)
        
        if self.current_node.parent:
            back_btn = Button(390, y_start, 150, 40, "Go Back", YELLOW, BLACK)
            buttons.append(("back", back_btn))
            back_btn.draw(self.screen)
        
        # Explore room button
        explore_btn = Button(SCREEN_WIDTH//2 - 100, y_start + 60, 200, 50, "Explore Room", GREEN, WHITE)
        buttons.append(("explore", explore_btn))
        explore_btn.draw(self.screen)
        
        # Inventory button
        inv_btn = Button(SCREEN_WIDTH - 200, 20, 180, 40, "Inventory", PURPLE, WHITE)
        buttons.append(("inventory", inv_btn))
        inv_btn.draw(self.screen)
        
        return buttons

    def draw_hero_stats(self):
        stats_x = 20
        stats_y = 80
        
        health_text = self.small_font.render(f"Health: {self.hero.health}/{self.hero.max_health}", True, WHITE)
        self.screen.blit(health_text, (stats_x, stats_y))
        
        strength_text = self.small_font.render(f"Strength: {self.hero.strength}", True, WHITE)
        self.screen.blit(strength_text, (stats_x, stats_y + 25))
        
        protection_text = self.small_font.render(f"Protection: {self.hero.protection}", True, WHITE)
        self.screen.blit(protection_text, (stats_x, stats_y + 50))
        
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = stats_x + 250
        bar_y = stats_y
        
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.hero.health / self.hero.max_health
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

    def draw_combat(self):
        self.screen.fill(RED)
        
        # Monster info
        monster_text = self.font.render(f"Fighting: {self.current_monster.name}", True, WHITE)
        monster_rect = monster_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(monster_text, monster_rect)
        
        # Monster health bar
        bar_width = 300
        bar_height = 30
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 150
        
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.current_monster.health / self.current_monster.max_health
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        monster_health_text = self.small_font.render(
            f"{self.current_monster.health}/{self.current_monster.max_health}", 
            True, WHITE
        )
        health_text_rect = monster_health_text.get_rect(center=(SCREEN_WIDTH//2, bar_y + bar_height + 20))
        self.screen.blit(monster_health_text, health_text_rect)
        
        # Hero stats
        self.draw_hero_stats()
        
        # Combat buttons
        attack_btn = Button(SCREEN_WIDTH//2 - 200, 400, 120, 50, "Attack", RED, WHITE)
        defend_btn = Button(SCREEN_WIDTH//2 - 60, 400, 120, 50, "Defend", BLUE, WHITE)
        run_btn = Button(SCREEN_WIDTH//2 + 80, 400, 120, 50, "Run", YELLOW, BLACK)
        inventory_btn = Button(SCREEN_WIDTH//2 - 60, 470, 120, 50, "Inventory", PURPLE, WHITE)
        
        buttons = [
            ("attack", attack_btn),
            ("defend", defend_btn), 
            ("run", run_btn),
            ("inventory", inventory_btn)
        ]
        
        for _, btn in buttons:
            btn.draw(self.screen)
        
        return buttons

    def draw_inventory(self):
        self.screen.fill(BLUE)
        
        title = self.font.render("Inventory & Equipment", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw inventory items
        inv_y = 100
        inv_text = self.small_font.render("Inventory:", True, WHITE)
        self.screen.blit(inv_text, (50, inv_y))
        
        for i, item in enumerate(self.hero.inventory):
            item_text = self.small_font.render(f"- {item}", True, WHITE)
            self.screen.blit(item_text, (70, inv_y + 30 + i * 25))
        
        # Draw equipment
        equip_y = 300
        equip_text = self.small_font.render("Equipment:", True, WHITE)
        self.screen.blit(equip_text, (50, equip_y))
        
        for i, (slot, item) in enumerate(self.hero.equip.items()):
            slot_text = f"{slot}: {item if item else 'None'}"
            equip_item_text = self.small_font.render(slot_text, True, WHITE)
            self.screen.blit(equip_item_text, (70, equip_y + 30 + i * 25))
        
        # Potion buttons
        potion_buttons = []
        if "Potion" in self.hero.inventory:
            potion_btn = Button(SCREEN_WIDTH - 300, 150, 150, 40, "Use Potion", GREEN, WHITE)
            potion_buttons.append(("Potion", potion_btn))
            potion_btn.draw(self.screen)
        
        if "Med_Potion" in self.hero.inventory:
            med_potion_btn = Button(SCREEN_WIDTH - 300, 200, 150, 40, "Use Med Potion", GREEN, WHITE)
            potion_buttons.append(("Med_Potion", med_potion_btn))
            med_potion_btn.draw(self.screen)
        
        if "Super_Potion" in self.hero.inventory:
            super_potion_btn = Button(SCREEN_WIDTH - 300, 250, 150, 40, "Use Super Potion", GREEN, WHITE)
            potion_buttons.append(("Super_Potion", super_potion_btn))
            super_potion_btn.draw(self.screen)
        
        back_btn = Button(50, SCREEN_HEIGHT - 100, 100, 50, "Back", GRAY, BLACK)
        potion_buttons.append(("back", back_btn))
        back_btn.draw(self.screen)
        
        return potion_buttons

    def draw_chest(self):
        self.screen.fill(GOLD)
        
        title = self.font.render("You found a chest!", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        if self.current_chest_item:
            item_text = self.font.render(f"Contains: {self.current_chest_item}", True, BLACK)
            item_rect = item_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(item_text, item_rect)
        
        take_btn = Button(SCREEN_WIDTH//2 - 100, 400, 200, 50, "Take Item", GREEN, WHITE)
        leave_btn = Button(SCREEN_WIDTH//2 - 100, 470, 200, 50, "Leave", RED, WHITE)
        
        buttons = [("take", take_btn), ("leave", leave_btn)]
        for _, btn in buttons:
            btn.draw(self.screen)
        
        return buttons

    def draw_message(self):
        if self.message and self.message_timer > 0:
            message_surface = self.font.render(self.message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            
            # Draw background
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
            self.screen.blit(message_surface, message_rect)
            
            self.message_timer -= self.clock.get_time()
            if self.message_timer <= 0:
                self.message = ""

    def explore_room(self):
        if self.current_node.visited:
            self.show_message("This room has already been explored.")
            return
        
        self.current_node.visited = True
        
        if self.current_node.data == "Boss Room":
            self.current_monster = Monster("Dragon", 200, 30, 10)
            self.state = GameState.COMBAT
            self.show_message("You encountered the Boss Dragon!")
        else:
            # Weighted random choice - chests are more common than monsters
            room_event = random.choices(
                ["chest", "monster", "empty"], 
                weights=[50, 20, 30], 
                k=1
            )[0]
            
            if room_event == "chest":
                random_item_category = np.random.choice(chest)
                self.current_chest_item = np.random.choice(list(random_item_category.keys()))
                self.current_chest_category = random_item_category
                self.state = GameState.CHEST
            elif room_event == "monster":
                self.current_monster = random.choice(self.monsters)
                self.current_monster.reset_health()
                self.state = GameState.COMBAT
                self.show_message(f"You encountered a {self.current_monster.name}!")
            else:
                self.show_message("The room is empty.")

    def handle_combat_action(self, action):
        if action == "attack":
            damage = self.hero.attack(self.current_monster)
            self.show_message(f"You deal {damage} damage!")
            
            if self.current_monster.health <= 0:
                defeated_monster_name = self.current_monster.name  # Store name before clearing
                if self.current_monster.name == "Dragon":
                    self.boss_defeated = True
                    self.state = GameState.VICTORY
                else:
                    self.state = GameState.PLAYING
                    self.current_monster = None
                self.show_message(f"You defeated the {defeated_monster_name}!")
                return
        
        elif action == "defend":
            self.hero.health += 10
            if self.hero.health > self.hero.max_health:
                self.hero.health = self.hero.max_health
            self.show_message("You defend and recover some health!")
        
        elif action == "run":
            if self.current_monster.name != "Dragon":  # Can't run from boss
                self.state = GameState.PLAYING
                self.current_monster = None
                self.show_message("You ran away!")
                return
            else:
                self.show_message("You cannot run from the boss!")
        
        # Monster attacks back
        if self.current_monster and self.current_monster.health > 0:
            damage = self.current_monster.attack(self.hero)
            self.show_message(f"The {self.current_monster.name} deals {damage} damage to you!")
            
            if self.hero.health <= 0:
                self.state = GameState.GAME_OVER

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == GameState.MENU:
                    start_btn, quit_btn = self.draw_menu()
                    start_btn.handle_event(event)
                    quit_btn.handle_event(event)
                    
                    if start_btn.handle_event(event):
                        self.state = GameState.PLAYING
                    elif quit_btn.handle_event(event):
                        self.running = False
                
                elif self.state == GameState.PLAYING:
                    buttons = self.draw_game()
                    
                    for action, btn in buttons:
                        btn.handle_event(event)
                        if btn.handle_event(event):
                            if action == "left":
                                self.current_node = self.current_node.left
                            elif action == "right":
                                self.current_node = self.current_node.right
                            elif action == "back":
                                self.current_node = self.current_node.parent
                            elif action == "explore":
                                self.explore_room()
                            elif action == "inventory":
                                self.state = GameState.INVENTORY
                
                elif self.state == GameState.COMBAT:
                    buttons = self.draw_combat()
                    
                    for action, btn in buttons:
                        btn.handle_event(event)
                        if btn.handle_event(event):
                            if action == "inventory":
                                self.state = GameState.INVENTORY
                            else:
                                self.handle_combat_action(action)
                
                elif self.state == GameState.INVENTORY:
                    buttons = self.draw_inventory()
                    
                    for action, btn in buttons:
                        btn.handle_event(event)
                        if btn.handle_event(event):
                            if action == "back":
                                if self.current_monster:
                                    self.state = GameState.COMBAT
                                else:
                                    self.state = GameState.PLAYING
                            elif action in ["Potion", "Med_Potion", "Super_Potion"]:
                                heal = self.hero.use_potion(action)
                                self.show_message(f"You healed {heal} health!")
                
                elif self.state == GameState.CHEST:
                    buttons = self.draw_chest()
                    
                    for action, btn in buttons:
                        btn.handle_event(event)
                        if btn.handle_event(event):
                            if action == "take":
                                if self.current_chest_item in items:
                                    self.hero.inventory.append(self.current_chest_item)
                                    self.show_message(f"Added {self.current_chest_item} to inventory!")
                                else:
                                    self.hero.equipment(self.current_chest_item)
                                    self.show_message(f"Equipped {self.current_chest_item}!")
                            
                            self.state = GameState.PLAYING
                            self.current_chest_item = None
                
                elif self.state == GameState.GAME_OVER:
                    self.screen.fill(BLACK)
                    game_over_text = self.font.render("GAME OVER", True, RED)
                    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    self.screen.blit(game_over_text, game_over_rect)
                    
                    restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, WHITE)
                    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                    self.screen.blit(restart_text, restart_rect)
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.__init__()  # Restart game
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                
                elif self.state == GameState.VICTORY:
                    self.screen.fill(GOLD)
                    victory_text = self.font.render("VICTORY!", True, BLACK)
                    victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    self.screen.blit(victory_text, victory_rect)
                    
                    victory_msg = self.small_font.render("You defeated the Dragon Boss!", True, BLACK)
                    victory_msg_rect = victory_msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                    self.screen.blit(victory_msg, victory_msg_rect)
                    
                    restart_text = self.small_font.render("Press SPACE to play again or ESC to quit", True, BLACK)
                    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
                    self.screen.blit(restart_text, restart_rect)
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.__init__()  # Restart game
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False

            # Clear screen and draw current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.COMBAT:
                self.draw_combat()
            elif self.state == GameState.INVENTORY:
                self.draw_inventory()
            elif self.state == GameState.CHEST:
                self.draw_chest()
            
            self.draw_message()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()