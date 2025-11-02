import random

class Game:
    def __init__(self):
        # Cards
        self.cards = [
            {"name": "Archers", "mana_cost": 3, "damage": 50},
            {"name": "Knight", "mana_cost": 3, "damage": 100},
            {"name": "Giant", "mana_cost": 5, "damage": 200},
            {"name": "Fireball", "mana_cost": 4, "damage": 150},
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

    def play_card(self, card_index):
        if self.winner:
            return

        chosen_card = self.cards[card_index]
        if self.player_mana >= chosen_card["mana_cost"]:
            self.player_mana -= chosen_card["mana_cost"]
            self.ai_hp -= chosen_card["damage"]
            self._check_for_winner()
            return True
        return False

    def ai_turn(self):
        if self.winner:
            return

        playable_cards = [card for card in self.cards if card["mana_cost"] <= self.ai_mana]
        if playable_cards:
            best_card = max(playable_cards, key=lambda card: card["damage"])
            self.ai_mana -= best_card["mana_cost"]
            self.player_hp -= best_card["damage"]
            self._check_for_winner()
            return best_card
        return None

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
