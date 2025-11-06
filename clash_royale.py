import random
import math
import pygame # For time tracking

class Troop:
    def __init__(self, card, owner, start_pos):
        self.name = card["name"]
        self.hp = card["hp"]
        self.max_hp = card["hp"]
        self.tower_damage = card["tower_damage"]
        self.attack_damage = card["attack_damage"]
        self.attack_range = card["attack_range"]
        self.attack_cooldown = card["attack_cooldown"]
        self.last_attack_time = 0
        self.speed = card["speed"]
        self.owner = owner
        self.x, self.y = start_pos
        self.path = []
        self.target_troop = None
        self.is_attacking_tower = False

    def attack(self, target):
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.hp -= self.attack_damage
            self.last_attack_time = current_time
            return target.hp <= 0
        return False

    def move(self):
        # Move towards the target
        if self.target_troop or self.is_attacking_tower or not self.path:
            return False # Don't move if attacking or no path

        target_x, target_y = self.path[0]

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            return False # Not yet at waypoint
        else:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
            return not self.path # Return True if path is complete

class Game:
    def __init__(self):
        # Cards
        self.cards = [
            {"name": "Knight", "mana_cost": 3, "hp": 500, "tower_damage": 100, "attack_damage": 100, "attack_range": 20, "attack_cooldown": 1.0, "speed": 2.5},
            {"name": "Giant", "mana_cost": 5, "hp": 2000, "tower_damage": 200, "attack_damage": 50, "attack_range": 20, "attack_cooldown": 1.5, "speed": 1.5},
            {"name": "Archers", "mana_cost": 3, "hp": 200, "tower_damage": 50, "attack_damage": 70, "attack_range": 100, "attack_cooldown": 0.8, "speed": 2.5},
            # Fireball is instant, so it has no troop stats
            {"name": "Fireball", "mana_cost": 4, "tower_damage": 150, "speed": 0},
        ]

        # Game constants
        self.player_tower_hp = 2500
        self.ai_tower_hp = 2500
        self.starting_mana = 5
        self.mana_regen = 1

        # Arena constants
        self.river_y = 300
        self.bridges = [(90, 300), (310, 300)]

        # Tower stats
        self.tower_attack_damage = 75
        self.tower_attack_range = 150
        self.tower_attack_cooldown = 0.8
        self.player_tower_last_attack_time = 0
        self.ai_tower_last_attack_time = 0

        # Game state
        self.player_hp = self.player_tower_hp
        self.ai_hp = self.ai_tower_hp
        self.player_mana = self.starting_mana
        self.ai_mana = self.starting_mana
        self.winner = None
        self.player_troops = []
        self.ai_troops = []
        self.player_trophies = 0
        self.last_match_trophies = 0

    def reset(self):
        self.player_hp = self.player_tower_hp
        self.ai_hp = self.ai_tower_hp
        self.player_mana = self.starting_mana
        self.ai_mana = self.starting_mana
        self.winner = None
        self.player_troops = []
        self.ai_troops = []
        self.last_match_trophies = 0

    def play_card(self, card_index, position):
        if self.winner:
            return False

        chosen_card = self.cards[card_index]
        if self.player_mana >= chosen_card["mana_cost"]:
            self.player_mana -= chosen_card["mana_cost"]
            if chosen_card["name"] == "Fireball":
                # Assuming AI tower is at a fixed position for now
                # This logic will be improved later
                self.ai_hp -= chosen_card["tower_damage"]
                self._check_for_winner()
            else:
                troop = Troop(chosen_card, "player", position)
                self.player_troops.append(troop)
            return True
        return False

    def ai_turn(self):
        if self.winner:
            return

        if self.player_trophies >= 200:
            self._advanced_ai_turn()
        elif self.player_trophies >= 100:
            self._strategic_ai_turn()
        else:
            self._simple_ai_turn()

    def _simple_ai_turn(self):
        playable_cards = [card for card in self.cards if card["mana_cost"] <= self.ai_mana]
        if playable_cards:
            best_card = max(playable_cards, key=lambda card: card.get("tower_damage", 0) + card.get("attack_damage", 0))
            self.ai_mana -= best_card["mana_cost"]
            if best_card["name"] == "Fireball":
                self.player_hp -= best_card["tower_damage"]
                self._check_for_winner()
            else:
                start_pos = (random.randint(150, 250), 150)
                troop = Troop(best_card, "ai", start_pos)
                self.ai_troops.append(troop)
            return best_card
        return None

    def _strategic_ai_turn(self):
        # Defensive logic
        threatening_troops = [t for t in self.player_troops if t.y < self.river_y]
        if threatening_troops:
            best_defensive_card = None
            # Find a card that can counter the threat
            for card in self.cards:
                if card['mana_cost'] <= self.ai_mana and card.get('attack_damage', 0) > 0:
                    best_defensive_card = card
                    break # Simple logic: use the first available troop

            if best_defensive_card:
                self.ai_mana -= best_defensive_card['mana_cost']
                # Place troop defensively
                start_pos = (threatening_troops[0].x, threatening_troops[0].y + 30)
                troop = Troop(best_defensive_card, "ai", start_pos)
                self.ai_troops.append(troop)
                return best_defensive_card

        # If no threats, play offensively (simple logic for now)
        return self._simple_ai_turn()

    def _advanced_ai_turn(self):
        # Defensive logic with archers
        threatening_troops = [t for t in self.player_troops if t.y < self.river_y]
        if threatening_troops:
            archers_card = next((card for card in self.cards if card["name"] == "Archers"), None)
            if archers_card and archers_card['mana_cost'] <= self.ai_mana:
                self.ai_mana -= archers_card['mana_cost']
                # Place archers defensively
                start_pos = (threatening_troops[0].x, threatening_troops[0].y + 50)
                troop = Troop(archers_card, "ai", start_pos)
                self.ai_troops.append(troop)
                return archers_card

        # If archers can't be played or no threats, fall back to strategic AI
        return self._strategic_ai_turn()

    def update(self):
        # Update player troops
        for troop in self.player_troops[:]:
            # Find closest enemy troop
            closest_enemy = None
            closest_dist = float('inf')
            for enemy in self.ai_troops:
                dist = math.hypot(troop.x - enemy.x, troop.y - enemy.y)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = enemy

            if closest_enemy:
                troop.is_attacking_tower = False
                troop.path = self._get_path((troop.x, troop.y), (closest_enemy.x, closest_enemy.y))
                if closest_dist <= troop.attack_range:
                    troop.target_troop = closest_enemy
                    if troop.attack(closest_enemy):
                        self.ai_troops.remove(closest_enemy)
                        troop.target_troop = None # Retarget next frame
                else:
                    troop.target_troop = None
                    troop.move()
            else: # No enemies left, target tower
                troop.target_troop = None
                troop.path = self._get_path((troop.x, troop.y), (200, 80)) # AI Tower pos
                if not troop.is_attacking_tower:
                    troop.is_attacking_tower = troop.move()

                if troop.is_attacking_tower:
                    current_time = pygame.time.get_ticks() / 1000
                    if current_time - troop.last_attack_time >= troop.attack_cooldown:
                        self.ai_hp -= troop.tower_damage
                        troop.last_attack_time = current_time
                        self._check_for_winner()

        # Tower attacks
        target_player = self._tower_attack(self.ai_troops, self.player_troops, "ai")
        target_ai = self._tower_attack(self.player_troops, self.ai_troops, "player")

        # Update AI troops
        for troop in self.ai_troops[:]:
            # Find closest enemy troop
            closest_enemy = None
            closest_dist = float('inf')
            for enemy in self.player_troops:
                dist = math.hypot(troop.x - enemy.x, troop.y - enemy.y)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = enemy

            if closest_enemy:
                troop.is_attacking_tower = False
                troop.path = self._get_path((troop.x, troop.y), (closest_enemy.x, closest_enemy.y))
                if closest_dist <= troop.attack_range:
                    troop.target_troop = closest_enemy
                    if troop.attack(closest_enemy):
                        self.player_troops.remove(closest_enemy)
                        troop.target_troop = None
                else:
                    troop.target_troop = None
                    troop.move()
            else: # No enemies left, target tower
                troop.target_troop = None
                troop.path = self._get_path((troop.x, troop.y), (200, 520)) # Player Tower pos
                if not troop.is_attacking_tower:
                    troop.is_attacking_tower = troop.move()

                if troop.is_attacking_tower:
                    current_time = pygame.time.get_ticks() / 1000
                    if current_time - troop.last_attack_time >= troop.attack_cooldown:
                        self.player_hp -= troop.tower_damage
                        troop.last_attack_time = current_time
                        self._check_for_winner()

        return target_player, target_ai

    def regenerate_mana(self):
        self.player_mana += self.mana_regen
        self.ai_mana += self.mana_regen

    def _check_for_winner(self):
        if self.winner: # Already decided
            return

        trophy_change = random.randint(27, 33)
        if self.player_hp <= 0:
            self.winner = "AI"
            self.last_match_trophies = -min(trophy_change, self.player_trophies)
            self.player_trophies += self.last_match_trophies
        elif self.ai_hp <= 0:
            self.winner = "Player"
            self.last_match_trophies = trophy_change
            self.player_trophies += self.last_match_trophies

    def _get_path(self, start_pos, target_pos):
        path = []
        # If crossing river
        if (start_pos[1] < self.river_y and target_pos[1] > self.river_y) or \
           (start_pos[1] > self.river_y and target_pos[1] < self.river_y):
            # Find closest bridge
            closest_bridge = min(self.bridges, key=lambda b: math.hypot(start_pos[0] - b[0], start_pos[1] - b[1]))
            path.append(closest_bridge)

        path.append(target_pos)
        return path

    def _tower_attack(self, friendly_troops, enemy_troops, owner):
        tower_pos = (200, 520) if owner == "player" else (200, 80)
        last_attack_time = self.player_tower_last_attack_time if owner == "player" else self.ai_tower_last_attack_time

        current_time = pygame.time.get_ticks() / 1000
        if current_time - last_attack_time < self.tower_attack_cooldown:
            return

        closest_enemy = None
        closest_dist = float('inf')
        for enemy in enemy_troops:
            dist = math.hypot(tower_pos[0] - enemy.x, tower_pos[1] - enemy.y)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = enemy

        if closest_enemy and closest_dist <= self.tower_attack_range:
            closest_enemy.hp -= self.tower_attack_damage
            if owner == "player":
                self.player_tower_last_attack_time = current_time
            else:
                self.ai_tower_last_attack_time = current_time

            if closest_enemy.hp <= 0:
                enemy_troops.remove(closest_enemy)
            return closest_enemy
        return None


def main_text():
    """Main function for the text-based game."""
    game = Game()

    print("Welcome to Simplified Clash Royale!")

    while not game.winner:
        print(f"\nPlayer HP: {game.player_hp}, Player Mana: {game.player_mana}")
        print(f"AI HP: {game.ai_hp}, AI Mana: {game.ai_mana}")

        print("\nAvailable Cards:")
        for i, card in enumerate(game.cards):
            damage = card.get('tower_damage', card.get('attack_damage', 0))
            print(f"{i + 1}. {card['name']} (Cost: {card['mana_cost']}, Damage: {damage})")

        try:
            choice = int(input("Choose a card to play (1-4): ")) - 1
            if 0 <= choice < len(game.cards):
                if not game.play_card(choice):
                    print("Not enough mana!")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        if game.winner:
            break

        game.ai_turn()
        game.regenerate_mana()

    print(f"\n{game.winner} wins!")


if __name__ == "__main__":
    main_text()
