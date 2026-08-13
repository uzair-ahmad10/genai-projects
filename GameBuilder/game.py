import pygame
import sys

# ==============================================================================
# CONSTANTS & CONFIGURATION
# ==============================================================================

# Screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700  # Extra space for status bar
BOARD_SIZE = 3
CELL_SIZE = SCREEN_WIDTH // BOARD_SIZE
LINE_WIDTH = 10
STATUS_BAR_HEIGHT = SCREEN_HEIGHT - SCREEN_WIDTH

# Colors (R, G, B)
BG_COLOR = (28, 32, 40)           # Dark charcoal
LINE_COLOR = (52, 61, 76)         # Muted blue-grey
X_COLOR = (239, 83, 80)           # Material Red 500
O_COLOR = (76, 175, 80)           # Material Green 500
TEXT_COLOR = (238, 238, 238)      # Near white
WIN_LINE_COLOR = (255, 193, 7)    # Amber/Yellow
BUTTON_COLOR = (52, 61, 76)
BUTTON_HOVER_COLOR = (69, 80, 98)
BUTTON_TEXT_COLOR = (238, 238, 238)

# Shapes
CROSS_WIDTH = 15
CIRCLE_WIDTH = 15
CIRCLE_RADIUS = CELL_SIZE // 3
OFFSET = CELL_SIZE // 4  # Padding inside cell for drawing shapes

# Game State
PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = None

# ==============================================================================
# HELPER CLASSES
# ==============================================================================

class Button:
    """Simple UI Button for Restart/Quit."""
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        # border_radius requires Pygame 2.0+
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, LINE_COLOR, self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class TicTacToe:
    """Encapsulates all game logic and rendering."""
    def __init__(self, screen):
        self.screen = screen
        # Use default system font with fallback for cross-platform compatibility
        self.font_large = pygame.font.SysFont('segoeui', 80, bold=True)
        self.font_medium = pygame.font.SysFont('segoeui', 40, bold=True)
        self.font_small = pygame.font.SysFont('segoeui', 28)
        self.font_status = pygame.font.SysFont('segoeui', 36, bold=True)
        
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.winning_line = None # ((r1, c1), (r2, c2))
        
        # UI Buttons
        btn_w, btn_h = 180, 50
        gap = 20
        total_w = 2 * btn_w + gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        btn_y = SCREEN_WIDTH + (STATUS_BAR_HEIGHT - btn_h) // 2
        
        self.restart_btn = Button(start_x, btn_y, btn_w, btn_h, "Restart", self.font_medium, self.reset_game)
        self.quit_btn = Button(start_x + btn_w + gap, btn_y, btn_w, btn_h, "Quit", self.font_medium, self.quit_game)

    def reset_game(self):
        """Resets board state for a new round."""
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.winning_line = None

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        """Processes mouse click on the board grid."""
        if self.game_over:
            return

        x, y = pos
        # Ignore clicks in status bar area
        if y >= SCREEN_WIDTH:
            return

        row = y // CELL_SIZE
        col = x // CELL_SIZE

        # Boundary check (defensive, though pos math should guarantee 0-2)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return

        if self.board[row][col] == EMPTY:
            self.board[row][col] = self.current_player
            if self.check_win(row, col):
                self.game_over = True
                self.winner = self.current_player
            elif self.is_board_full():
                self.game_over = True
                self.winner = 'Draw'
            else:
                self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def check_win(self, row, col):
        """Checks all win conditions from the last move. Returns True if win."""
        player = self.board[row][col]
        
        # Check Row
        if all(self.board[row][c] == player for c in range(BOARD_SIZE)):
            self.winning_line = ((row, 0), (row, BOARD_SIZE - 1))
            return True
        
        # Check Col
        if all(self.board[r][col] == player for r in range(BOARD_SIZE)):
            self.winning_line = ((0, col), (BOARD_SIZE - 1, col))
            return True
        
        # Check Main Diagonal (Top-Left to Bottom-Right)
        if row == col:
            if all(self.board[i][i] == player for i in range(BOARD_SIZE)):
                self.winning_line = ((0, 0), (BOARD_SIZE - 1, BOARD_SIZE - 1))
                return True
        
        # Check Anti Diagonal (Top-Right to Bottom-Left)
        if row + col == BOARD_SIZE - 1:
            if all(self.board[i][BOARD_SIZE - 1 - i] == player for i in range(BOARD_SIZE)):
                self.winning_line = ((0, BOARD_SIZE - 1), (BOARD_SIZE - 1, 0))
                return True
                
        return False

    def is_board_full(self):
        return all(self.board[r][c] != EMPTY for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def draw_lines(self):
        """Draws the static grid lines."""
        for i in range(1, BOARD_SIZE):
            # Vertical
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_WIDTH), LINE_WIDTH)
            # Horizontal
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (0, i * CELL_SIZE), (SCREEN_WIDTH, i * CELL_SIZE), LINE_WIDTH)

    def draw_figures(self):
        """Draws X's and O's based on board state."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                player = self.board[row][col]
                if player == EMPTY:
                    continue
                
                center_x = col * CELL_SIZE + CELL_SIZE // 2
                center_y = row * CELL_SIZE + CELL_SIZE // 2
                
                if player == PLAYER_X:
                    # Draw X (two crossing lines)
                    start_desc = (col * CELL_SIZE + OFFSET, row * CELL_SIZE + OFFSET)
                    end_desc = (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET)
                    start_asc = (col * CELL_SIZE + OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET)
                    end_asc = (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + OFFSET)
                    
                    pygame.draw.line(self.screen, X_COLOR, start_desc, end_desc, CROSS_WIDTH)
                    pygame.draw.line(self.screen, X_COLOR, start_asc, end_asc, CROSS_WIDTH)
                
                elif player == PLAYER_O:
                    # Draw O (circle)
                    pygame.draw.circle(self.screen, O_COLOR, (center_x, center_y), CIRCLE_RADIUS, CIRCLE_WIDTH)

    def draw_winning_line(self):
        """Draws a strikethrough line across the winning combination."""
        if not self.winning_line:
            return
        
        (r1, c1), (r2, c2) = self.winning_line
        
        # Calculate pixel centers of start and end cells
        start_pos = (c1 * CELL_SIZE + CELL_SIZE // 2, r1 * CELL_SIZE + CELL_SIZE // 2)
        end_pos = (c2 * CELL_SIZE + CELL_SIZE // 2, r2 * CELL_SIZE + CELL_SIZE // 2)
        
        # Extend line slightly past cell centers for visual flair
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = max(1, (dx**2 + dy**2)**0.5)
        norm_dx, norm_dy = dx / dist, dy / dist
        extension = CELL_SIZE // 2
        
        final_start = (start_pos[0] - norm_dx * extension, start_pos[1] - norm_dy * extension)
        final_end = (end_pos[0] + norm_dx * extension, end_pos[1] + norm_dy * extension)
        
        pygame.draw.line(self.screen, WIN_LINE_COLOR, final_start, final_end, LINE_WIDTH + 5)

    def draw_status_bar(self):
        """Draws the bottom UI: Turn indicator or Winner text + Buttons."""
        # Background for status bar
        pygame.draw.rect(self.screen, (22, 26, 33), (0, SCREEN_WIDTH, SCREEN_WIDTH, STATUS_BAR_HEIGHT))
        # Separator line
        pygame.draw.line(self.screen, LINE_COLOR, (0, SCREEN_WIDTH), (SCREEN_WIDTH, SCREEN_WIDTH), 3)
        
        if self.game_over:
            if self.winner == 'Draw':
                text = "It's a Draw!"
                color = TEXT_COLOR
            else:
                text = f"Player {self.winner} Wins!"
                color = X_COLOR if self.winner == PLAYER_X else O_COLOR
        else:
            text = f"Player {self.current_player}'s Turn"
            color = X_COLOR if self.current_player == PLAYER_X else O_COLOR
        
        text_surf = self.font_status.render(text, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_WIDTH + 40))
        self.screen.blit(text_surf, text_rect)
        
        # Draw Buttons
        self.restart_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def update(self, events):
        """Main update loop: handle events, draw everything."""
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            
            # Pass events to buttons
            self.restart_btn.handle_event(event)
            self.quit_btn.handle_event(event)

        # Rendering
        self.screen.fill(BG_COLOR)
        self.draw_lines()
        self.draw_figures()
        if self.game_over and self.winner != 'Draw':
            self.draw_winning_line()
        self.draw_status_bar()
        pygame.display.update()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    pygame.init()
    pygame.display.set_caption("Tic Tac Toe - PyGame Edition")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    game = TicTacToe(screen)
    
    running = True
    while running:
        events = pygame.event.get()
        game.update(events)
        clock.tick(60) # Cap at 60 FPS

if __name__ == "__main__":
    main()