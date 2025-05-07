import copy
import random
import pygame
from piece import Piece
#from hexlib import HexGrid  # Import the hexlib library
from hexgrid import HexGrid




# Initialize Pygame
pygame.init()

# Initialize the mixer module for sound
pygame.mixer.init()

powerup_sound = pygame.mixer.Sound("powerup_sound.mp3")  # Replace with your actual sound file

class InvalidMoveException(Exception):
    pass

class PowerUp:
    UNDO = 'undomove'
    DOUBLE = 'double_score'
    WILD = 'wildcard'

class Board:
    AXES = [
        (( 0, -1), ( 0,  1)),
        ((-1,  1), ( 1, -1)),
        ((-1,  0), ( 1,  0)),
    ]

    def __init__(self, rows, cols, hex_spacing_x, hex_height, hex_radius, grid_x, grid_y):
        self.rows = rows
        self.cols = cols
        self.grid = HexGrid(rows, cols, hex_spacing_x, hex_height, hex_radius, grid_x, grid_y)
        self.powerups = [[None for _ in range(cols)] for _ in range(rows)]
        self.current_turn_moves = []
        self.previous_state = copy.deepcopy(self.grid)
        self.history = [copy.deepcopy(self.grid)]
        self.double_score_enabled = False
        self.bypass_rules = False
        self._spawn_powerups()

    def _spawn_powerups(self):
        types = [PowerUp.UNDO, PowerUp.DOUBLE, PowerUp.WILD]
        free_cells = self.grid.get_empty_cells()
        for pu in types:
            r, c = random.choice(free_cells)
            free_cells.remove((r, c))
            self.powerups[r][c] = pu

    def get_powerup_at(self, row, col):
        return self.powerups[row][col]

    def clear_powerup(self, row, col):
        self.powerups[row][col] = None

    def start_turn(self):
        self.previous_state = copy.deepcopy(self.grid)
        self.current_turn_moves.clear()
        self.double_score_enabled = False
        self.bypass_rules = False

    def reset_turn(self):
        self.grid = copy.deepcopy(self.previous_state)
        self.current_turn_moves.clear()
        self.double_score_enabled = False
        self.bypass_rules = False

    def place_piece(self, row, col, piece):
        if not self.grid.is_valid_position(row, col):
            raise InvalidMoveException("Move out of board boundaries.")
        if self.grid.is_occupied(row, col):
            raise InvalidMoveException("Space is already occupied.")

        pu = self.get_powerup_at(row, col)

        if pu == PowerUp.WILD:
            self.bypass_rules = True
            self.clear_powerup(row, col)
            powerup_sound.play()
        else:
            if not self._is_adjacent_valid(row, col, piece):
                raise InvalidMoveException("Move must be adjacent to existing tiles.")
            if not self._validate_line(row, col, piece):
                raise InvalidMoveException("Piece placement breaks cohesion rules.")

        before_score = self.score_current_turn()
        self.grid.place_tile(row, col, piece)
        self.current_turn_moves.append((row, col, piece))

        if pu == PowerUp.UNDO:
            self.clear_powerup(row, col)
            if len(self.history) >= 2:
                self.history.pop()
                self.grid = copy.deepcopy(self.history[-1])

            self.current_turn_moves.clear()
            self.double_score_enabled = False
            self.bypass_rules = False
            powerup_sound.play()
            return 0

        after_score = self.score_current_turn()
        earned = after_score - before_score
        if pu == PowerUp.DOUBLE:
            earned *= 2
            self.clear_powerup(row, col)
            self.double_score_enabled = False
            powerup_sound.play()

        return earned

    def get_valid_moves(self, piece):
        valid = []
        snapshot_grid = copy.deepcopy(self.grid)
        snapshot_moves = list(self.current_turn_moves)
        snapshot_double = self.double_score_enabled
        snapshot_bypass = self.bypass_rules
        snapshot_powerups = copy.deepcopy(self.powerups)

        for r in range(self.rows):
            for c in range(self.cols):
                if snapshot_grid.get(r, c) is None:
                    self.grid = copy.deepcopy(snapshot_grid)
                    self.current_turn_moves = list(snapshot_moves)
                    self.double_score_enabled = snapshot_double
                    self.bypass_rules = snapshot_bypass
                    self.powerups = copy.deepcopy(snapshot_powerups)

                    if self._is_adjacent_valid(r, c, piece) and self._validate_line(r, c, piece):
                        valid.append((r, c))

        self.grid = snapshot_grid
        self.current_turn_moves = snapshot_moves
        self.double_score_enabled = snapshot_double
        self.bypass_rules = snapshot_bypass
        self.powerups = snapshot_powerups
        return valid

    def check_for_full_board(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid.get(r, c) is None:
                    return False
        return True

    def _is_adjacent_valid(self, row, col, new_piece):
        if self.grid.is_empty() and not self.current_turn_moves:
            return True

        if not self.current_turn_moves:
            for (dr1, dc1), (dr2, dc2) in self.AXES:
                for dr, dc in ((dr1, dc1), (dr2, dc2)):
                    nr, nc = row + dr, col + dc
                    if self.grid.is_valid_position(nr, nc):
                        neighbor = self.grid.get(nr, nc)
                        if neighbor and (neighbor.color == new_piece.color or neighbor.shape == new_piece.shape):
                            return True
            return False

        for pr, pc, placed in self.current_turn_moves:
            if (row, col) in self.grid.get_neighbors(pr, pc):
                if placed.color == new_piece.color or placed.shape == new_piece.shape:
                    return True
        return False

    def score_current_turn(self):
        total = 0
        counted = set()
        for r, c, _ in self.current_turn_moves:
            for axis_idx in range(len(self.AXES)):
                length, positions = self._calculate_line_score(r, c, axis_idx)
                newpos = positions - counted
                total += len(newpos)
                counted |= newpos
                if length == 6:
                    total += 6
        if self.double_score_enabled:
            total *= 2
        return total

    def end_turn(self):
        self.current_turn_moves.clear()
        self.double_score_enabled = False
        self.bypass_rules = False
        self.history.append(copy.deepcopy(self.grid))

    def _validate_line(self, row, col, piece):
        if self.bypass_rules:
            return True

        for (dr1, dc1), (dr2, dc2) in self.AXES:
            line = [piece]
            r, c = row + dr1, col + dc1
            while self.grid.is_valid_position(r, c) and self.grid.get(r, c):
                line.insert(0, self.grid.get(r, c))
                r += dr1; c += dc1
            r, c = row + dr2, col + dc2
            while self.grid.is_valid_position(r, c) and self.grid.get(r, c):
                line.append(self.grid.get(r, c))
                r += dr2; c += dc2

            if not self._check_cohesion(line):
                return False

        return True

    def _check_cohesion(self, line):
        if len(line) <= 1:
            return True
        colors = {p.color for p in line}
        shapes = {p.shape for p in line}
        return (len(colors) == 1 and len(shapes) == len(line)) or (len(shapes) == 1 and len(colors) == len(line))

    def _calculate_line_score(self, row, col, axis_idx):
        (dr1, dc1), (dr2, dc2) = self.AXES[axis_idx]
        positions = {(row, col)}

        r, c = row + dr1, col + dc1
        while self.grid.is_valid_position(r, c) and self.grid.get(r, c):
            positions.add((r, c))
            r += dr1; c += dc1

        r, c = row + dr2, col + dc2
        while self.grid.is_valid_position(r, c) and self.grid.get(r, c):
            positions.add((r, c))
            r += dr2; c += dc2

        return len(positions), positions