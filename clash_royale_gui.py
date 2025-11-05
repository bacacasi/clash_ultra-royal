import pygame
import sys
from clash_royale import Game

# --- Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (34, 139, 34)  # Forest Green
RIVER_COLOR = (65, 105, 225)  # Royal Blue
PATH_COLOR = (184, 134, 11)   # Dark Goldenrod
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

class Projectile:
    def __init__(self, start_pos, target_troop):
        self.x, self.y = start_pos
        self.target_troop = target_troop
        self.speed = 10

    def move(self):
        dx = self.target_troop.x - self.x
        dy = self.target_troop.y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist < self.speed:
            return True # Reached target

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        return False


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
        self.projectiles = []
        self.game_state = 'start_screen'

    def _draw_projectiles(self):
        for p in self.projectiles[:]:
            if p.move():
                self.projectiles.remove(p)
            else:
                pygame.draw.circle(self.screen, (255, 255, 0), (int(p.x), int(p.y)), 5)

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
            damage = card.get('tower_damage', card.get('attack_damage', 0))
            damage_text = self.font.render(f"DMG: {damage}", True, (0,0,0))

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
            damage = card.get('tower_damage', card.get('attack_damage', 0))
            damage_text = self.font.render(f"DMG: {damage}", True, (0,0,0))

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
        pos = (int(troop.x), int(troop.y))
        size = 10 # Default size

        if troop.name == "Knight":
            size = 12
            # Body
            pygame.draw.rect(self.screen, color, (pos[0] - size, pos[1] - size, size*2, size*2))
            # Head
            pygame.draw.circle(self.screen, color, (pos[0], pos[1] - size - 5), 5)
            # Sword
            pygame.draw.line(self.screen, (192, 192, 192), (pos[0] + size, pos[1]), (pos[0] + size + 10, pos[1] - 10), 3)
        elif troop.name == "Giant":
            size = 20
            # Body
            pygame.draw.circle(self.screen, color, pos, size)
            # Head
            pygame.draw.circle(self.screen, color, (pos[0], pos[1] - size - 8), 8)
        elif troop.name == "Archers":
            size = 10
            # Body
            points = [(pos[0], pos[1] - size), (pos[0] - size, pos[1] + size), (pos[0] + size, pos[1] + size)]
            pygame.draw.polygon(self.screen, color, points)
            # Head
            pygame.draw.circle(self.screen, color, (pos[0], pos[1] - size - 5), 5)
            # Bow
            pygame.draw.arc(self.screen, (139, 69, 19), [pos[0]+5, pos[1]-10, 10, 20], 1.57, 4.71, 2)


        # Draw HP bar for troop
        hp_percentage = troop.hp / troop.max_hp
        hp_bar_width = size * 2 * hp_percentage
        hp_bar_height = 5
        hp_bar_x = pos[0] - size
        hp_bar_y = pos[1] - size - 15
        pygame.draw.rect(self.screen, (255,0,0), (hp_bar_x, hp_bar_y, size * 2, hp_bar_height))
        pygame.draw.rect(self.screen, (0,255,0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))


    def _handle_input(self, event):
        if self.game_state == 'start_screen':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.combat_button_rect.collidepoint(event.pos):
                    self.game.reset()
                    self.game_state = 'playing'
                elif self.quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        elif self.game_state == 'game_over':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.game.reset()
                    self.game_state = 'start_screen'
        elif self.game_state == 'playing':
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
        # Draw river
        pygame.draw.rect(self.screen, RIVER_COLOR, (0, SCREEN_HEIGHT // 2 - 30, SCREEN_WIDTH, 60))

        # Draw paths
        pygame.draw.rect(self.screen, PATH_COLOR, (50, SCREEN_HEIGHT // 2, 80, SCREEN_HEIGHT // 2))
        pygame.draw.rect(self.screen, PATH_COLOR, (SCREEN_WIDTH - 130, SCREEN_HEIGHT // 2, 80, SCREEN_HEIGHT // 2))
        pygame.draw.rect(self.screen, PATH_COLOR, (50, 0, 80, SCREEN_HEIGHT // 2))
        pygame.draw.rect(self.screen, PATH_COLOR, (SCREEN_WIDTH - 130, 0, 80, SCREEN_HEIGHT // 2))

        # Draw bridges
        pygame.draw.rect(self.screen, BRIDGE_COLOR, (50, SCREEN_HEIGHT // 2 - 10, 80, 20))
        pygame.draw.rect(self.screen, BRIDGE_COLOR, (SCREEN_WIDTH - 130, SCREEN_HEIGHT // 2 - 10, 80, 20))

        # Draw towers with crenellations
        self._draw_tower_with_crenellations(PLAYER_TOWER_POS, PLAYER_TOWER_COLOR)
        self._draw_tower_with_crenellations(AI_TOWER_POS, AI_TOWER_COLOR)

    def _draw_tower_with_crenellations(self, pos, color):
        tower_rect = pygame.Rect(pos[0] - TOWER_SIZE[0] // 2, pos[1] - TOWER_SIZE[1] // 2, TOWER_SIZE[0], TOWER_SIZE[1])
        pygame.draw.rect(self.screen, color, tower_rect)

        # Crenellations
        for i in range(4):
            cren_x = tower_rect.left + i * (TOWER_SIZE[0] / 4) + 5
            cren_y = tower_rect.top - 10
            pygame.draw.rect(self.screen, color, (cren_x, cren_y, 10, 10))

    def _draw_game_over_screen(self):
        self._draw_gradient_background()

        # Display result
        result_text = "Victoire !" if self.game.winner == "Player" else "Défaite"
        trophy_text = f"Trophées: {self.game.last_match_trophies:+#}"

        result_font = pygame.font.SysFont(None, 72)
        result_surface = result_font.render(result_text, True, (255, 255, 0))
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        self.screen.blit(result_surface, result_rect)

        trophy_font = pygame.font.SysFont(None, 48)
        trophy_surface = trophy_font.render(trophy_text, True, WHITE)
        trophy_rect = trophy_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(trophy_surface, trophy_rect)

        # Back to menu button
        self.menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT * 3 // 4 - 25, 200, 50)
        pygame.draw.rect(self.screen, (255, 255, 0), self.menu_button_rect) # Yellow border
        pygame.draw.rect(self.screen, (0, 0, 0), self.menu_button_rect.inflate(-5, -5))
        menu_text = self.font.render("Menu Principal", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=self.menu_button_rect.center)
        self.screen.blit(menu_text, menu_text_rect)

    def _draw_gradient_background(self):
        top_color = (0, 0, 139) # Dark Blue
        bottom_color = (135, 206, 250) # Light Sky Blue
        for y in range(SCREEN_HEIGHT):
            color = [
                top_color[i] + (bottom_color[i] - top_color[i]) * y / SCREEN_HEIGHT
                for i in range(3)
            ]
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def _draw_start_screen(self):
        self._draw_gradient_background()

        # Draw title
        title_font = pygame.font.SysFont(None, 72)
        title_text = title_font.render("Clash Royale", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # Display trophies
        trophy_font = pygame.font.SysFont(None, 36)
        trophy_text = f"Trophées: {self.game.player_trophies}"
        trophy_surface = trophy_font.render(trophy_text, True, WHITE)
        trophy_rect = trophy_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75))
        self.screen.blit(trophy_surface, trophy_rect)

        # Draw buttons
        self.combat_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50)
        self.quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)

        # Combat button
        pygame.draw.rect(self.screen, (255, 255, 0), self.combat_button_rect) # Yellow border
        pygame.draw.rect(self.screen, (0, 0, 0), self.combat_button_rect.inflate(-5, -5))
        combat_text = self.font.render("Combat", True, (255, 255, 255))
        combat_text_rect = combat_text.get_rect(center=self.combat_button_rect.center)
        self.screen.blit(combat_text, combat_text_rect)

        # Quit button
        pygame.draw.rect(self.screen, (255, 255, 0), self.quit_button_rect) # Yellow border
        pygame.draw.rect(self.screen, (0, 0, 0), self.quit_button_rect.inflate(-5, -5))
        quit_text = self.font.render("Quitter", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)


    def run(self):
        running = True
        clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 1000) # Timer for AI turn and mana regen

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.game_state == 'playing' and event.type == pygame.USEREVENT:
                    if not self.game.winner:
                        played_card = self.game.ai_turn()
                        if played_card:
                            self.ai_last_played_card = played_card
                            self.ai_card_display_timer = 60 # Display for 60 frames
                        self.game.regenerate_mana()

                self._handle_input(event)

            if self.game_state == 'playing':
                if not self.game.winner:
                    target_player, target_ai = self.game.update()
                    if target_player:
                        self.projectiles.append(Projectile(AI_TOWER_POS, target_player))
                    if target_ai:
                        self.projectiles.append(Projectile(PLAYER_TOWER_POS, target_ai))

            # --- Drawing ---
            if self.game_state == 'start_screen':
                self._draw_start_screen()
            elif self.game_state == 'playing':
                self.screen.fill(BACKGROUND_COLOR)
                self._draw_arena()
                self._draw_game_state()
                self._draw_cards()
                self._draw_ai_card()
                self._draw_dragging_card()
                self._draw_troops()
                self._draw_projectiles()

            if self.game.winner:
                self.game_state = 'game_over'

            if self.game_state == 'game_over':
                self._draw_game_over_screen()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_logic = Game()
    game_gui = GameGUI(game_logic)
    game_gui.run()
