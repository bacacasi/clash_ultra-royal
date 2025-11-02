import random
import time

# Cards
CARDS = [
    {"name": "Archers", "mana_cost": 3, "damage": 50},
    {"name": "Knight", "mana_cost": 3, "damage": 100},
    {"name": "Giant", "mana_cost": 5, "damage": 200},
    {"name": "Fireball", "mana_cost": 4, "damage": 150},
]

# Game constants
PLAYER_TOWER_HP = 1000
AI_TOWER_HP = 1000
STARTING_MANA = 5
MANA_REGEN = 1

# Game state
player_hp = PLAYER_TOWER_HP
ai_hp = AI_TOWER_HP
player_mana = STARTING_MANA
ai_mana = STARTING_MANA

def main():
    """Main game loop."""
    global player_hp, ai_hp, player_mana, ai_mana

    print("Welcome to Simplified Clash Royale!")

    while player_hp > 0 and ai_hp > 0:
        # Player's turn
        print(f"\nPlayer HP: {player_hp}, Player Mana: {player_mana}")
        print(f"AI HP: {ai_hp}, AI Mana: {ai_mana}")

        print("\nAvailable Cards:")
        for i, card in enumerate(CARDS):
            print(f"{i + 1}. {card['name']} (Cost: {card['mana_cost']}, Damage: {card['damage']})")

        try:
            choice = int(input("Choose a card to play (1-4): ")) - 1
            if 0 <= choice < len(CARDS):
                chosen_card = CARDS[choice]
                if player_mana >= chosen_card["mana_cost"]:
                    player_mana -= chosen_card["mana_cost"]
                    ai_hp -= chosen_card["damage"]
                    print(f"You played {chosen_card['name']}, dealing {chosen_card['damage']} damage!")
                else:
                    print("Not enough mana!")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        if ai_hp <= 0:
            break

        # AI's turn
        time.sleep(1)
        # Basic AI logic: play the highest damage card it can afford
        playable_cards = [card for card in CARDS if card["mana_cost"] <= ai_mana]
        if playable_cards:
            # Find the card with the most damage among the playable ones
            best_card = max(playable_cards, key=lambda card: card["damage"])
            ai_mana -= best_card["mana_cost"]
            player_hp -= best_card["damage"]
            print(f"\nAI played {best_card['name']}, dealing {best_card['damage']} damage!")
        else:
            print("\nAI has no playable cards.")

        # Mana regeneration
        player_mana += MANA_REGEN
        ai_mana += MANA_REGEN

    # Game over
    if player_hp <= 0:
        print("\nAI wins!")
    else:
        print("\nPlayer wins!")

if __name__ == "__main__":
    main()
