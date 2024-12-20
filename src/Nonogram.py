import pygame
import copy

from src.config import WHITE


class Nonogram:
    def __init__(self, grid, row_clues, col_clues):
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.player_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_size = 30
        self.grid_offset = (100, 100)
        self.font = pygame.font.Font(None, 24)
        self.history = []
        self.redo_stack = []

    @classmethod
    def from_level_data(cls, level_data):
        return cls(level_data['grid'], level_data['row_clues'], level_data['col_clues'])

    def draw(self, screen):
        self.draw_grid(screen)
        self.draw_clues(screen)
        self.draw_cells(screen)

    def get_max_clue_dimensions(self):
        font = pygame.font.Font(None, 24)

        max_row_clue_width = max(font.size(" ".join(map(str, row_clue)))[0] for row_clue in self.row_clues) + 25

        max_col_clue_height = max(sum(font.size(str(num))[1] for num in col_clue) for col_clue in self.col_clues) + 25

        return max_row_clue_width, max_col_clue_height

    def draw_grid(self, screen):
        screen_width, screen_height = screen.get_size()
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        clue_width, clue_height = self.get_max_clue_dimensions()
        self.grid_offset = (
            (screen_width - grid_width) // 2,
            (screen_height - grid_height) // 2
        )

        grid_rect = pygame.Rect(self.grid_offset[0] - clue_width, self.grid_offset[1] - clue_height, grid_width + clue_width, grid_height + clue_height)
        pygame.draw.rect(screen, WHITE, grid_rect)

        for i in range(self.rows + 1):
            start_pos = (self.grid_offset[0] - clue_width, self.grid_offset[1] + i * self.cell_size)
            end_pos = (self.grid_offset[0] + self.cols * self.cell_size, self.grid_offset[1] + i * self.cell_size)
            pygame.draw.line(screen, (0, 0, 0), start_pos, end_pos, 2)

        for j in range(self.cols + 1):
            start_pos = (self.grid_offset[0] + j * self.cell_size, self.grid_offset[1] - clue_height)
            end_pos = (self.grid_offset[0] + j * self.cell_size, self.grid_offset[1] + self.rows * self.cell_size)
            pygame.draw.line(screen, (0, 0, 0), start_pos, end_pos, 2)

        start_pos_x = (self.grid_offset[0] - clue_width, self.grid_offset[1] - clue_height)
        end_pos_x = (self.grid_offset[0] - clue_width, self.grid_offset[1] + self.rows * self.cell_size)
        pygame.draw.line(screen, (0, 0, 0), start_pos_x, end_pos_x, 2)

        start_pos_y = (self.grid_offset[0] - clue_width, self.grid_offset[1] - clue_height)
        end_pos_y = (self.grid_offset[0] + self.cols * self.cell_size, self.grid_offset[1] - clue_height)
        pygame.draw.line(screen, (0, 0, 0), start_pos_y, end_pos_y, 2)

    def draw_clues(self, screen):
        row_clue_surfaces = [
            (self.font.render(" ".join(map(str, row_clue)), True, (0, 0, 0)), i)
            for i, row_clue in enumerate(self.row_clues)
        ]

        for text_surface, i in row_clue_surfaces:
            screen.blit(text_surface, (
                self.grid_offset[0] - 10 - text_surface.get_width(),
                self.grid_offset[1] + i * self.cell_size + self.cell_size // 2 - text_surface.get_height() // 2
            ))

        col_clue_surfaces = [
            ([
                 self.font.render(str(num), True, (0, 0, 0)) for num in col_clue
             ], j) for j, col_clue in enumerate(self.col_clues)
        ]
        for text_surfaces, j in col_clue_surfaces:
            total_height = sum(surface.get_height() for surface in text_surfaces)
            current_y = self.grid_offset[1] - 10 - total_height
            for surface in text_surfaces:
                screen.blit(surface, (
                    self.grid_offset[0] + j * self.cell_size + self.cell_size // 2 - surface.get_width() // 2,
                    current_y
                ))
                current_y += surface.get_height()

    def draw_cells(self, screen):
        for i in range(self.rows):
            for j in range(self.cols):
                cell_rect = pygame.Rect(
                    self.grid_offset[0] + j * self.cell_size,
                    self.grid_offset[1] + i * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                if self.player_grid[i][j] == 1:
                    pygame.draw.rect(screen, (0, 0, 0), cell_rect)
                elif self.player_grid[i][j] == 2:
                    pygame.draw.line(screen, (255, 0, 0), cell_rect.topleft, cell_rect.bottomright, 2)
                    pygame.draw.line(screen, (255, 0, 0), cell_rect.topright, cell_rect.bottomleft, 2)

    def set_cell(self, row, col, value):
        self.history.append((row, col, self.player_grid[row][col]))
        if self.player_grid[row][col] in {1, 2}:
            self.player_grid[row][col] = 0
        else:
            self.player_grid[row][col] = value
            self.redo_stack.clear()

    def undo(self):
        if self.history:
            row, col, previous_state = self.history.pop()
            self.redo_stack.append((row, col, self.player_grid[row][col]))
            self.player_grid[row][col] = previous_state

    def redo(self):
        if self.redo_stack:
            row, col, next_state = self.redo_stack.pop()
            self.history.append((row, col, self.player_grid[row][col]))
            self.player_grid[row][col] = next_state

    def is_solved(self):
        playergrid_copy = copy.deepcopy(self.player_grid)

        for l in range(self.rows):
            for i in range(self.cols):
                if playergrid_copy[l][i] == 2:
                    playergrid_copy[l][i] = 0
        return playergrid_copy == self.grid

    def get_hint(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.player_grid[row][col] != self.grid[row][col]:
                    return row, col, self.grid[row][col]
        return None

    @staticmethod
    def get_row_clue(row):
        clue = []
        count = 0
        for cell in row:
            if cell == 1:
                count += 1
            elif count > 0:
                clue.append(count)
                count = 0
        if count > 0:
            clue.append(count)
        return clue if clue else None
