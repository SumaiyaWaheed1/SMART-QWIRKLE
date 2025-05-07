import math



class HexGrid:

    CUBE_DIRS = [
        (+1, -1,  0), (+1,  0, -1), ( 0, +1, -1),
        (-1, +1,  0), (-1,  0, +1), ( 0, -1, +1),
    ]

    def __init__(self, rows, cols, hex_spacing_x, hex_height, hex_radius, grid_x, grid_y):
        self.rows       = rows
        self.cols       = cols
        self.grid       = [[None]*cols for _ in range(rows)]
        self.HEX_SPACING_X = hex_spacing_x
        self.HEX_HEIGHT    = hex_height
        self.HEX_RADIUS    = hex_radius
        self.GRID_X        = grid_x
        self.GRID_Y        = grid_y

    @staticmethod
    def _axial_to_cube(q, r):
        x = q; z = r; y = -x - z
        return x, y, z

    @staticmethod
    def _cube_to_axial(x, y, z):
        return x, z

    def get_neighbors(self, row, col):
        # 1) convert odd‑q to “true” axial
        q = col
        r = row - (col - (col & 1)) // 2

        # 2) lift to cube coords
        x, y, z = HexGrid._axial_to_cube(q, r)

        nbrs = []
        for dx, dy, dz in HexGrid.CUBE_DIRS:
            nx, ny, nz = x+dx, y+dy, z+dz
            # 3) back to axial
            nq, nr = HexGrid._cube_to_axial(nx, ny, nz)
            # 4) axial → odd‑q offset
            ncol = int(nq)
            nrow = int(nr + (nq - (nq & 1)) // 2)
            if 0 <= nrow < self.rows and 0 <= ncol < self.cols:
                nbrs.append((nrow, ncol))

        return nbrs


    def is_valid_position(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_empty(self):
        return all(cell is None for row in self.grid for cell in row)


    def is_occupied(self, r, c):
        return self.grid[r][c] is not None

    def place_tile(self, r, c, tile):
        if self.is_valid_position(r, c):
            self.grid[r][c] = tile

    def get(self, r, c):
        return self.grid[r][c] if self.is_valid_position(r, c) else None

    def get_empty_cells(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] is None]

    # def get_neighbors(self, r, c):
    #     """
    #     Return the six neighbors for odd‑q flat‑topped hex layout.
    #     Even columns use one offset set, odd columns another.
    #     """
    #     if c % 2 == 0:  # even column
    #         directions = [
    #             (-1, -1),  # up‑left
    #             (-1,  0),  # up‑right
    #             ( 0, -1),  # left
    #             ( 0,  1),  # right
    #             ( 1, -1),  # down‑left
    #             ( 1,  0),  # down‑right
    #         ]
    #     else:  # odd column
    #         directions = [
    #             (-1,  0),  # up‑left
    #             (-1,  1),  # up‑right
    #             ( 0, -1),  # left
    #             ( 0,  1),  # right
    #             ( 1,  0),  # down‑left
    #             ( 1,  1),  # down‑right
    #         ]

    #     neighbors = []
    #     for dr, dc in directions:
    #         nr, nc = r + dr, c + dc
    #         if self.is_valid_position(nr, nc):
    #             neighbors.append((nr, nc))
    #     return neighbors

    # def get_neighbors(self, r, c):
    #     x, y, z = self.offset_to_cube(r, c)
    #     result = []
    #     for dx, dy, dz in [
    #         ( 1, -1,  0), (-1,  1,  0),
    #         ( 1,  0, -1), (-1,  0,  1),
    #         ( 0,  1, -1), ( 0, -1,  1),
    #     ]:
    #         nr, nc = self.cube_to_offset(x+dx, y+dy, z+dz)
    #         if self.is_valid_position(nr, nc):
    #             result.append((nr, nc))
    #     return result


    def get_hex_position(self, row, col):
        x = col*(self.HEX_RADIUS*3/2) + self.GRID_X + self.HEX_RADIUS
        y = row*self.HEX_HEIGHT + (col&1)*(self.HEX_HEIGHT/2) + self.GRID_Y + self.HEX_RADIUS
        return x, y

    def pixel_to_hex(self, px, py):
        # 1) move into hex‐local origin
        x = px - (self.GRID_X + self.HEX_RADIUS)
        y = py - (self.GRID_Y + self.HEX_RADIUS)

        # 2) un‐rotate into axial
        q = (2/3 * x) / self.HEX_RADIUS
        r = ((-1/3 * x) + (math.sqrt(3)/3 * y)) / self.HEX_RADIUS

        # 3) axial → cube
        cx, cz = q, r
        cy = -cx - cz

        # 4) round cube
        rx, ry, rz = round(cx), round(cy), round(cz)
        x_diff, y_diff, z_diff = abs(rx-cx), abs(ry-cy), abs(rz-cz)
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        # 5) back to odd‑q offset
        col = int(rx)
        row = int(rz + (rx - (rx & 1)) // 2)
        return row, col



    # def pixel_to_hex(self, x, y):
    #     # 1) Which column band are we in?
    #     #    floor((x - left_margin) / horizontal_spacing)
    #     col = int((x - self.GRID_X) / self.HEX_SPACING_X)

    #     # 2) Remove that column’s vertical shift, then pick the row band
    #     y_off = y - self.GRID_Y - (col & 1) * (self.HEX_HEIGHT / 2)
    #     row  = int(y_off / self.HEX_HEIGHT)

    #     return row, col
    
    def offset_to_cube(self, r, c):
        # odd‐q vertical layout → cube
        x = c
        z = r - (c - (c & 1)) // 2
        y = -x - z
        return x, y, z

    def cube_to_offset(self, x, y, z):
        # cube → odd‐q vertical offset
        c = x
        r = z + (x - (x & 1)) // 2
        return r, c