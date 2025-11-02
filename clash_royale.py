import random
import math

class Troop:
    def __init__(self, card, owner, start_pos, target_pos):
        self.name = card["name"]
        self.damage = card["damage"]
        self.speed = card["speed"]
        self.owner = owner
        self.x, self.y = start_pos
        self.target_x, self.target_y = target_pos

    def move(self):
        # Move towards the target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            return False # Not yet at target
        else:
            self.x = self.target_x
            self.y = self.target_y
            return True # Reached target

class Game:
    def __init__(self):
        # Cards
        self.cards = [
            {"name": "Knight", "mana_cost": 3, "damage": 100, "speed": 2.5},
            {"name": "Giant", "mana_cost": 5, "damage": 200, "speed": 1.5},
            {"name": "Archers", "mana_cost": 3, "damage": 50, "speed": 2.5},
            # Fireball is instant, so we'll handle it differently later
            {"name": "Fireball", "mana_cost": 4, "damage": 150, "speed": 0},
        ]

        # Game constants
        self.player_tower_hp = 1000
        self.ai_tower_hp = 1000
        self.starting_mana = 5
        self.mana_regen = 1

        # Game state
        self.player_hp = self.player_tower_hp
        self.ai_hp = self.ai_tower_hp
        self.player_mana = self.starting_mana
        self.ai_mana = self.starting_mana
        self.winner = None
        self.player_troops = []
        self.ai_troops = []

    def play_card(self, card_index, position):
        if self.winner:
            return False

        chosen_card = self.cards[card_index]
        if self.player_mana >= chosen_card["mana_cost"]:
            self.player_mana -= chosen_card["mana_cost"]
            if chosen_card["name"] == "Fireball":
                # Assuming AI tower is at a fixed position for now
                # This logic will be improved later
                self.ai_hp -= chosen_card["damage"]
                self._check_for_winner()
            else:
                # Target AI tower
                troop = Troop(chosen_card, "player", position, (200, 80))
                self.player_troops.append(troop)
            return True
        return False

    def ai_turn(self):
        if self.winner:
            return

        playable_cards = [card for card in self.cards if card["mana_cost"] <= self.ai_mana]
        if playable_cards:
            best_card = max(playable_cards, key=lambda card: card["damage"])
            self.ai_mana -= best_card["mana_cost"]
            if best_card["name"] == "Fireball":
                self.player_hp -= best_card["damage"]
                self._check_for_winner()
            else:
                # Spawn troop near AI tower and target player tower
                start_pos = (random.randint(150, 250), 150)
                troop = Troop(best_card, "ai", start_pos, (200, 520))
                self.ai_troops.append(troop)
            return best_card
        return None

    def update(self):
        # Move player troops and deal damage
        for troop in self.player_troops[:]:
            if troop.move():
                self.ai_hp -= troop.damage
                self.player_troops.remove(troop)
                self._check_for_winner()

        # Move AI troops and deal damage
        for troop in self.ai_troops[:]:
            if troop.move():
                self.player_hp -= troop.damage
                self.ai_troops.remove(troop)
                self._check_for_winner()

    def regenerate_mana(self):
        self.player_mana += self.mana_regen
        self.ai_mana += self.mana_regen

    def _check_for_winner(self):
        if self.player_hp <= 0:
            self.winner = "AI"
        elif self.ai_hp <= 0:
            self.winner = "Player"

def main_text():
    """Main function for the text-based game."""
    game = Game()

    print("Welcome to Simplified Clash Royale!")

    while not game.winner:
        print(f"\nPlayer HP: {game.player_hp}, Player Mana: {game.player_mana}")
        print(f"AI HP: {game.ai_hp}, AI Mana: {game.ai_mana}")

        print("\nAvailable Cards:")
        for i, card in enumerate(game.cards):
            print(f"{i + 1}. {card['name']} (Cost: {card['mana_cost']}, Damage: {card['damage']})")

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
