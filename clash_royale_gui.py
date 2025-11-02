import pygame
import sys
from clash_royale import Game

# --- Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (34, 139, 34)  # Forest Green
BRIDGE_COLOR = (139, 69, 19)  # Brown
PLAYER_TOWER_COLOR = (0, 0, 255) # Blue
AI_TOWER_COLOR = (255, 0, 0) # Red
PLAYER_TROOP_COLOR = (173, 216, 230) # Light Blue
AI_TROOP_COLOR = (255, 182, 193) # Light Red
HP_BAR_COLOR = (255, 255, 0) # Yellow
MANA_COLOR = (221, 160, 221) # Plum
WHITE = (255, 255, 255)
FONT_SIZE = 30
FPS = 60
CARD_AREA_HEIGHT = 120
CARD_WIDTH = 80
CARD_HEIGHT = 100
CARD_BG_COLOR = (200, 200, 200)

# --- Arena Layout ---
PLAYER_TOWER_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
AI_TOWER_POS = (SCREEN_WIDTH // 2, 80)
TOWER_SIZE = (60, 80)

# --- Troop Visuals ---
TROOP_VISUALS = {
    "Knight": {"shape": "square", "size": 12},
    "Giant": {"shape": "circle", "size": 20},
    "Archers": {"shape": "triangle", "size": 10},
}

# --- Main Game Class ---
class GameGUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Clash Royale")
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.card_rects = []
        self.ai_last_played_card = None
        self.ai_card_display_timer = 0
        self.dragging_card = None
        self.dragging_card_index = -1

    def _draw_ai_card(self):
        if self.ai_last_played_card and self.ai_card_display_timer > 0:
            card_area_y = 50
            x_pos = SCREEN_WIDTH // 2 - CARD_WIDTH // 2
            card_rect = pygame.Rect(x_pos, card_area_y, CARD_WIDTH, CARD_HEIGHT)

            # Draw card background
            pygame.draw.rect(self.screen, CARD_BG_COLOR, card_rect)

            # Draw card text
            card = self.ai_last_played_card
            name_text = self.font.render(card["name"], True, (0,0,0))
            cost_text = self.font.render(f"Cost: {card['mana_cost']}", True, (0,0,0))
            damage_text = self.font.render(f"DMG: {card['damage']}", True, (0,0,0))

            self.screen.blit(name_text, (x_pos + 5, card_area_y + 5))
            self.screen.blit(cost_text, (x_pos + 5, card_area_y + 35))
            self.screen.blit(damage_text, (x_pos + 5, card_area_y + 65))

            self.ai_card_display_timer -= 1


    def _draw_cards(self):
        self.card_rects = []
        card_area_y = SCREEN_HEIGHT - CARD_AREA_HEIGHT
        for i, card in enumerate(self.game.cards):
            x_pos = i * (CARD_WIDTH + 10) + 15
            card_rect = pygame.Rect(x_pos, card_area_y, CARD_WIDTH, CARD_HEIGHT)
            self.card_rects.append(card_rect)

            # Draw card background
            pygame.draw.rect(self.screen, CARD_BG_COLOR, card_rect)

            # Draw card text
            name_text = self.font.render(card["name"], True, (0,0,0))
            cost_text = self.font.render(f"Cost: {card['mana_cost']}", True, (0,0,0))
            damage_text = self.font.render(f"DMG: {card['damage']}", True, (0,0,0))

            self.screen.blit(name_text, (x_pos + 5, card_area_y + 5))
            self.screen.blit(cost_text, (x_pos + 5, card_area_y + 35))
            self.screen.blit(damage_text, (x_pos + 5, card_area_y + 65))

    def _draw_dragging_card(self):
        if self.dragging_card:
            mouse_pos = pygame.mouse.get_pos()
            card_rect = pygame.Rect(mouse_pos[0] - CARD_WIDTH // 2, mouse_pos[1] - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, CARD_BG_COLOR, card_rect)

            name_text = self.font.render(self.dragging_card["name"], True, (0,0,0))
            self.screen.blit(name_text, (card_rect.x + 5, card_rect.y + 5))

    def _draw_troops(self):
        for troop in self.game.player_troops:
            self._draw_troop(troop, PLAYER_TROOP_COLOR)
        for troop in self.game.ai_troops:
            self._draw_troop(troop, AI_TROOP_COLOR)

    def _draw_troop(self, troop, color):
        visuals = TROOP_VISUALS.get(troop.name)
        if not visuals:
            return # Don't draw if no visuals defined

        pos = (int(troop.x), int(troop.y))
        size = visuals["size"]

        if visuals["shape"] == "circle":
            pygame.draw.circle(self.screen, color, pos, size)
        elif visuals["shape"] == "square":
            rect = pygame.Rect(pos[0] - size, pos[1] - size, size * 2, size * 2)
            pygame.draw.rect(self.screen, color, rect)
        elif visuals["shape"] == "triangle":
            points = [(pos[0], pos[1] - size), (pos[0] - size, pos[1] + size), (pos[0] + size, pos[1] + size)]
            pygame.draw.polygon(self.screen, color, points)


    def _handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(event.pos):
                    self.dragging_card = self.game.cards[i]
                    self.dragging_card_index = i
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_card:
                # Player can only place troops on their side of the arena
                if event.pos[1] > SCREEN_HEIGHT // 2:
                    self.game.play_card(self.dragging_card_index, event.pos)
                self.dragging_card = None
                self.dragging_card_index = -1

    def _draw_game_state(self):
        # Draw HP bars
        player_hp_percentage = self.game.player_hp / self.game.player_tower_hp
        ai_hp_percentage = self.game.ai_hp / self.game.ai_tower_hp

        player_hp_bar_width = TOWER_SIZE[0] * player_hp_percentage
        ai_hp_bar_width = TOWER_SIZE[0] * ai_hp_percentage

        pygame.draw.rect(self.screen, HP_BAR_COLOR, (PLAYER_TOWER_POS[0] - TOWER_SIZE[0] // 2, PLAYER_TOWER_POS[1] - TOWER_SIZE[1] // 2 - 15, player_hp_bar_width, 10))
        pygame.draw.rect(self.screen, HP_BAR_COLOR, (AI_TOWER_POS[0] - TOWER_SIZE[0] // 2, AI_TOWER_POS[1] - TOWER_SIZE[1] // 2 - 15, ai_hp_bar_width, 10))

        # Draw Mana
        player_mana_text = self.font.render(f"Mana: {self.game.player_mana}", True, WHITE)
        ai_mana_text = self.font.render(f"Mana: {self.game.ai_mana}", True, WHITE)
        self.screen.blit(player_mana_text, (10, SCREEN_HEIGHT - 40))
        self.screen.blit(ai_mana_text, (10, 10))


    def _draw_arena(self):
        # Draw bridge
        pygame.draw.line(self.screen, BRIDGE_COLOR, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 10)

        # Draw towers
        player_tower_rect = pygame.Rect(PLAYER_TOWER_POS[0] - TOWER_SIZE[0] // 2, PLAYER_TOWER_POS[1] - TOWER_SIZE[1] // 2, TOWER_SIZE[0], TOWER_SIZE[1])
        pygame.draw.rect(self.screen, PLAYER_TOWER_COLOR, player_tower_rect)

        ai_tower_rect = pygame.Rect(AI_TOWER_POS[0] - TOWER_SIZE[0] // 2, AI_TOWER_POS[1] - TOWER_SIZE[1] // 2, TOWER_SIZE[0], TOWER_SIZE[1])
        pygame.draw.rect(self.screen, AI_TOWER_COLOR, ai_tower_rect)


    def run(self):
        running = True
        clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 1000) # Timer for AI turn and mana regen

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    if not self.game.winner:
                        played_card = self.game.ai_turn()
                        if played_card:
                            self.ai_last_played_card = played_card
                            self.ai_card_display_timer = 60 # Display for 60 frames
                        self.game.regenerate_mana()

                self._handle_input(event)

            if not self.game.winner:
                self.game.update()

            # --- Drawing ---
            self.screen.fill(BACKGROUND_COLOR)
            self._draw_arena()
            self._draw_game_state()
            self._draw_cards()
            self._draw_ai_card()
            self._draw_dragging_card()
            self._draw_troops()

            if self.game.winner:
                winner_text = self.font.render(f"{self.game.winner} wins!", True, WHITE)
                text_rect = winner_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                self.screen.blit(winner_text, text_rect)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_logic = Game()
    game_gui = GameGUI(game_logic)
    game_gui.run()
