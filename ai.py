import math
import copy
import random
from board import InvalidMoveException, PowerUp

class QwirkleAI:
    def __init__(self, name="QwirkleAI", difficulty="hard", max_depth=3):
        self.name = name
        self.difficulty = difficulty.lower()
        self.max_depth = max_depth
        self.tiles = []

    def set_tiles(self, tiles):
        self.tiles = tiles

    def get_tiles(self):
        return self.tiles

    def choose_move(self, board):
        if self.difficulty == "easy":
            return self.choose_move_easy(board)
        elif self.difficulty == "medium":
            return self.choose_move_medium(board)
        elif self.difficulty == "hard":
            return self.choose_move_hard(board)
        else:
            return self.choose_move_easy(board)

    def choose_move_easy(self, board):
        for r in range(board.grid.rows):
            for c in range(board.grid.cols):
                for i, tile in enumerate(self.tiles):
                    temp_board = copy.deepcopy(board)
                    try:
                        if self._is_adjacent_valid(r, c, temp_board):
                            temp_board.place_piece(r, c, tile)
                            return (r, c, i)
                    except InvalidMoveException:
                        continue
        return None

    def choose_move_medium(self, board):
        best_move = None
        best_score = -math.inf

        for r in range(board.grid.rows):
            for c in range(board.grid.cols):
                for i, tile in enumerate(self.tiles):
                    temp_board = copy.deepcopy(board)
                    try:
                        if self._is_adjacent_valid(r, c, temp_board):
                            temp_board.place_piece(r, c, tile)
                            score = temp_board.score_current_turn()

                            if board.get_powerup_at(r, c):
                                powerup = board.get_powerup_at(r, c)
                                if powerup == PowerUp.WILD:
                                    score += 20
                                elif powerup == PowerUp.DOUBLE:
                                    score += 15
                                elif powerup == PowerUp.UNDO:
                                    score += 10

                            if score > best_score:
                                best_score = score
                                best_move = (r, c, i)
                    except InvalidMoveException:
                        continue
        return best_move

    def choose_move_hard(self, board):
        all_moves = []
        for r in range(board.grid.rows):
            for c in range(board.grid.cols):
                for i, tile in enumerate(self.tiles):
                    temp_board = copy.deepcopy(board)
                    try:
                        if self._is_adjacent_valid(r, c, temp_board):
                            temp_board.place_piece(r, c, tile)
                            immediate_score = temp_board.score_current_turn()
                            all_moves.append((r, c, i, immediate_score))
                    except InvalidMoveException:
                        continue

        if not all_moves:
            return None

        best_move = None
        best_value = -math.inf

        for (r, c, tile_index, _) in all_moves:
            temp_board = copy.deepcopy(board)
            temp_board.place_piece(r, c, self.tiles[tile_index])
            value = self._minimax(temp_board, depth=self.max_depth, alpha=-math.inf, beta=math.inf, maximizing=False)
            if value > best_value:
                best_value = value
                best_move = (r, c, tile_index)
        return best_move

    def _minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0:
            score = board.score_current_turn()
            for r in range(board.grid.rows):
                for c in range(board.grid.cols):
                    powerup = board.get_powerup_at(r, c)
                    if powerup == PowerUp.WILD:
                        score += 50
                    elif powerup == PowerUp.DOUBLE:
                        score += 25
            return score

        if maximizing:
            max_eval = -math.inf
            score = board.score_current_turn()
            max_eval = max(max_eval, score)
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                return max_eval
            return max_eval
        else:
            min_eval = board.score_current_turn()
            beta = min(beta, min_eval)
            if beta <= alpha:
                return min_eval
            return min_eval

    def _is_adjacent_valid(self, r, c, board):
        neighbors = board.grid.get_neighbors(r, c)
        for nr, nc in neighbors:
            if board.grid.get(nr, nc) is not None:
                return True
        return False