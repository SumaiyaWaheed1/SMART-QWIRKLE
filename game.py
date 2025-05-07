import random
import sys
import os
import math
import pygame

from piece import COLORS, SHAPES, Piece
from board import Board, PowerUp, InvalidMoveException
from ai import QwirkleAI
from ui import HumanUI  # GUI wrapper for human moves

# Constants for GUI dimensions
CELL_SIZE = 100
BOARD_ROWS = 6
BOARD_COLS = 6
HEX_RADIUS = CELL_SIZE // 2
BOARD_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
HAND_HEIGHT = 100
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + HAND_HEIGHT

def hex_center(r, c):
    x = c * (HEX_RADIUS * 3/2) + HEX_RADIUS
    y = r * (math.sqrt(3) * HEX_RADIUS) + (c % 2) * (math.sqrt(3) * HEX_RADIUS / 2)
    return int(x), int(y)

def draw_hexagon_at(surface, x, y, radius, fill_color, outline_color=(0,0,0)):
    points = [
        (x + radius * math.cos(math.radians(a)),
         y + radius * math.sin(math.radians(a)))
        for a in range(0, 360, 60)
    ]
    pygame.draw.polygon(surface, fill_color, points)
    pygame.draw.polygon(surface, outline_color, points, 2)

class Game:
    def __init__(self, num_humans=1, num_ai=1, ai_difficulty="hard", rows=6, cols=6):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Qwirkle GUI")
        self.font_small = pygame.font.SysFont(None, 28)

        self.board = Board(rows, cols)
        self.bag_of_tiles = []
        self.players = []
        self._generate_bag_of_tiles()

        for h in range(num_humans):
            self.players.append(HumanUI(name=f"Human {h+1}"))
        for a in range(num_ai):
            self.players.append(QwirkleAI(name=f"AI {a+1}", difficulty=ai_difficulty, max_depth=3))

        self.current_player_idx = 0
        self.scores = {player.name: 0 for player in self.players}

        self.tiles_images = {}

        self.powerup_icons = {}
        pu_base = os.path.join(os.path.dirname(__file__), 'powerups')
        for typ in (PowerUp.UNDO, PowerUp.DOUBLE, PowerUp.WILD):
            path = os.path.join(pu_base, f"{typ}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.powerup_icons[typ] = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))
            except Exception as e:
                print(f"Error loading powerup '{typ}': {e}")

        self.human_moves = []
        self.ai_moves = []

    def deal_tiles(self, player, desired_count=6):
        while len(player.tiles) < desired_count and self.bag_of_tiles:
            player.tiles.append(self.bag_of_tiles.pop())

    def check_for_dead_end(self):
        human_moves = self.board.get_valid_moves(self.players[0].tiles)
        ai_moves = self.board.get_valid_moves(self.players[1].tiles)

        if not human_moves and not ai_moves:
            print("No valid moves left for both players. Game Over!")
            return True

        if self.board.check_for_full_board() and not human_moves and not ai_moves:
            print("The grid is full and no valid moves left. Game Over!")
            return True

        return False

    def run_game(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            player = self.players[self.current_player_idx]
            self.deal_tiles(player)
            self.board.start_turn()

            if isinstance(player, HumanUI):
                moves = player.take_turn(self.board, self.screen)
                for (r, c, tile) in moves:
                    try:
                        pts = self.board.place_piece(r, c, tile)
                        self.scores[player.name] += pts
                        self.draw_board(); pygame.display.flip()
                    except InvalidMoveException as e:
                        print(f"Human error: {e}")

            else:  # AI's turn
                self.board.start_turn()
                while True:
                    move = player.choose_move(self.board)
                    if not move:
                        break
                    r, c, i = move
                    tile = player.tiles[i]
                    try:
                        pts = self.board.place_piece(r, c, tile)
                        self.scores[player.name] += pts
                        player.tiles.pop(i)
                        self.draw_board(); pygame.display.flip()
                        pygame.time.wait(500)
                    except InvalidMoveException:
                        break

                # After AI's turn, check if it has valid moves
                if not self.board.get_valid_moves(player.get_tiles()):
                    # AI has no valid moves, so it will swap tiles
                    if len(player.get_tiles()) == 6:  # Only swap if AI has all 6 tiles
                        print("AI has no valid moves, swapping tiles...")
                        # Add the AI's current tiles back to the bag before swapping
                        bag.extend(player.get_tiles())

                        player.get_tiles().clear()  # Clear AI's tiles
                        player.get_tiles().extend(bag[:6])  # Refill AI's tiles from the bag
                        bag = bag[6:]  # Remove the swapped tiles from the bag

                        player.set_tiles(player.get_tiles())  # Update AI's tile list

                        # Switch turn to human after AI swaps tiles
                        self.board.end_turn()  # Ends AI's turn
                        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
                        continue  # Skip AI's turn and move to the next player (human)

                # Refill AI's tiles and continue the game
                while len(player.get_tiles()) < 6 and bag:
                    player.get_tiles().append(bag.pop())
                player.set_tiles(player.get_tiles())

            self.board.end_turn()
            self.draw_board()
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False

            # Check if the game has reached a dead-end or full grid
            if self.check_for_dead_end():
                self.end_game()
                break  # Exit the game loop if it's a dead-end

            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            clock.tick(30)

        pygame.quit()
        self._show_winner()
        sys.exit()



    def _show_winner(self):
        print("Game over! Scores:")
        for name, s in self.scores.items():
            print(f"{name}: {s}")

    def end_game(self):
        print("Game over!")
        self.display_winner()

    def display_winner(self):
        print(f"Winner: {self.get_winner()}")

    def get_winner(self):
        if self.scores[self.players[0].name] > self.scores[self.players[1].name]:
            return self.players[0].name
        elif self.scores[self.players[0].name] < self.scores[self.players[1].name]:
            return self.players[1].name
        else:
            return "Draw"