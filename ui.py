
import pygame
import sys
import os
import random
from board import Board, InvalidMoveException, PowerUp
from piece import Piece, COLORS, SHAPES
from ai import QwirkleAI
import random




# --- Constants ---
GRID_SIZE = 6
CELL_SIZE = 80
BOARD_WIDTH = GRID_SIZE * CELL_SIZE
BOARD_HEIGHT = GRID_SIZE * CELL_SIZE


GRID_Y = 50
NAME_AREA_HEIGHT = 40
HAND_AREA_HEIGHT = 120
TILE_GAP = 10


HIGHLIGHT = (65, 73, 92)
PAGE_BG = (15, 23, 42)
neon = (0,255,255)
RACK_X_OFFSET = 30
HAND_X = 0
MAX_RACK_SLOTS = 6
MAX_RACK_WIDTH = MAX_RACK_SLOTS * CELL_SIZE + (MAX_RACK_SLOTS - 1) * TILE_GAP


import math
HEX_RADIUS = CELL_SIZE // 2
HEX_WIDTH  = 2 * HEX_RADIUS
HEX_HEIGHT = math.sqrt(3) * HEX_RADIUS
HEX_SPACING_X = HEX_WIDTH * 3 / 4
HEX_SPACING_Y = HEX_HEIGHT





def draw_hexagon_at(surface, x, y, radius, fill_color, outline_color=(0,0,0)):
    points = [
        (x + radius * math.cos(math.radians(a)),
         y + radius * math.sin(math.radians(a)))
        for a in range(0, 360, 60)
    ]
    pygame.draw.polygon(surface, fill_color, points)
    pygame.draw.polygon(surface, outline_color, points, 2)




# --- Turn state flag ---
in_turn = False




# --- Pygame Init ---
pygame.init()
infoObject = pygame.display.Info()
screen_width = int(infoObject.current_w * 0.9)
screen_height = int(infoObject.current_h * 0.9)
WINDOW_WIDTH = screen_width
WINDOW_HEIGHT = screen_height
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Smart Qwirkle")
GRID_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2


clock = pygame.time.Clock()


try:
    font_large = pygame.font.Font('E:\\supreme-spike-font\\SupremeSpike-KVO8D.otf', 64)
    font_med = pygame.font.Font('E:\\supreme-spike-font\\SupremeSpike-KVO8D.otf', 36)
    font_small = pygame.font.Font('E:\\supreme-spike-font\\SupremeSpike-KVO8D.otf', 28)
except FileNotFoundError:
    print("Poppins font not found, using system fonts instead.")
    font_large = pygame.font.SysFont('montserratregular', 64)
    font_med = pygame.font.SysFont('montserratregular', 36)
    font_small = pygame.font.SysFont('montserratregular', 28)






# --- Layout Helper ---
def update_layout():
    global GRID_X, UI_Y, HAND_X
    GRID_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2
    UI_Y  = GRID_Y + BOARD_HEIGHT + 60
    tile_gap      = 10
    rack_slots    = 6
    rack_width    = rack_slots * CELL_SIZE + (rack_slots - 1) * tile_gap
    HAND_X = GRID_X + (BOARD_WIDTH - rack_width) // 2 - 100

    # Difficulty
    easy_btn.rect.topleft  = ((WINDOW_WIDTH - easy_btn.rect.width)//2, 300)
    med_btn.rect.topleft   = ((WINDOW_WIDTH - med_btn.rect.width)//2, 350)
    hard_btn.rect.topleft  = ((WINDOW_WIDTH - hard_btn.rect.width)//2, 400)
    name_input.rect.topleft = ((WINDOW_WIDTH - name_input.rect.width)//2, 300)
    next_btn.rect.topleft   = (name_input.rect.right + 10, name_input.rect.y)
    
    # Swap & Pass under your rack
    if state == 'game':
        rack_left = GRID_X
        rack_mid_y = UI_Y + HAND_AREA_HEIGHT//2
        
        swap_rect.topleft = (HAND_X- swap_rect.width -10,rack_mid_y - swap_rect.height//2)
        gap= 0
        turn_rect.topleft = (swap_rect.x, swap_rect.bottom + gap )
    else:
        # Hide the buttons by positioning them off-screen when not in 'game' state
        swap_rect.topleft = (-500, -500)
        turn_rect.topleft = (-500, -500)
        
        
class HumanUI:
    def __init__(self, name):
        self.name = name
        self.tiles = []  # List of tiles for the human player

    def take_turn(self, board, screen):
        moves = []
        # Code for detecting mouse clicks to select a tile and place it on the board
        # Returns the moves, e.g., a list of (row, col, tile)
        return moves
 
# --- Fullscreen Toggle ---
def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    update_layout()




# --- Sound ---
invalid_move_sound = pygame.mixer.Sound("invalid_move.mp3")

def get_ai_comment():
    comments = [
        "Well played!",
        "Nice move!",
        "Great strategy!",
        "Awesome placement!",
        "That’s a good one!",
        "Impressive!"
    ]
    return random.choice(comments)

def draw_ai_message(message):
    message_box = pygame.Rect(30, GRID_Y+80, 300, 80)
    #pygame.draw.rect(screen, neon, message_box, border_radius=12)
    #pygame.draw.rect(screen, (20, 20, 60), message_box, border_radius=12)
    msg_surf = font_small.render(message, True, (255,255,255))
    screen.blit(msg_surf, msg_surf.get_rect(center=message_box.center))

show_ai_message = False
ai_message = ""


# --- TextInput ---
class TextInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.text = ''
        self.active = False
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(ev.pos)
        if self.active and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += ev.unicode
    def draw(self, screen, font):
        pygame.draw.rect(screen, (255,255,255), self.rect)
        pygame.draw.rect(screen, (0,0,0), self.rect, 2)
        txt = font.render(self.text, True, (0,0,0))
        screen.blit(txt, (self.rect.x+5, self.rect.y+5))




# --- Load Tiles ---
def load_tile_images(path="tiles"):
    images = {}
    shape_map = {
        'TRIANGLE':'triangle','DIAMOND':'diamond','SQUARE':'square',
        'CIRCLE':'circle','STAR':'star','SPARKLE':'spiral'
    }
    scale_factor = 0.8# Adjust this value (0.7 to 0.8 is a good starting point)
    scaled_height = HEX_HEIGHT * scale_factor
    scaled_width = scaled_height # Maintain aspect ratio
    for ck in COLORS.__dict__:
        if not ck.isupper(): continue
        color = ck.lower()
        for sk, sc in SHAPES.__dict__.items():
            if sk not in shape_map: continue
            fn = f"{color}_{shape_map[sk]}.png"
            full = os.path.join(path, fn)
            try:
                img = pygame.image.load(full).convert_alpha()
                img = pygame.transform.scale(img, (int(scaled_width), int(scaled_height)))
                images[(color, sc)] = img
            except:
                pass
    return images

try:
    ai_icon = pygame.image.load("AI.png").convert_alpha()
    ai_icon = pygame.transform.scale(ai_icon, (32,32))

    human_icon = pygame.image.load("user.png").convert_alpha()
    human_icon = pygame.transform.scale(human_icon, (32,32))
except Exception as e:
    print("Failed to load score avatars:", e)
    # fallback to None so we can still draw text
    ai_icon = human_icon = None




tiles_images = load_tile_images()




# --- Load Power-up Icons ---
powerup_icons = {}
pu_dir = os.path.join(os.path.dirname(__file__), 'powerups')
for typ in (PowerUp.UNDO, PowerUp.DOUBLE, PowerUp.WILD):
    path = os.path.join(pu_dir, f"{typ}.png")
    try:
        img = pygame.image.load(path).convert_alpha()
        small = int(CELL_SIZE * 0.6)
        img = pygame.transform.scale(img, (small, small))
        powerup_icons[typ] = img
    except Exception as e:
        print(f"Failed to load powerup '{typ}': {e}")




# --- Button ---
class Button:
    def __init__(self, rect, text, font, color=(100, 200, 100), hover_color=(120, 220, 120)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovering = False
        self.select = False


    def draw(self, screen):
        # Check if the button is being hovered over
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.hovering = True
        else:
            self.hovering = False


        # Change color on hover
        button_color = self.hover_color if self.hovering else self.color


        # Draw the button with a gaming theme
        pygame.draw.rect(screen, button_color, self.rect, border_radius=10)  # Rounded corners
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 3, border_radius=10)  # Border with shadow


        # Set text color and render the text
        text_color = (125, 123, 142) if not self.hovering else (0, 0, 0)  # Inverted text color
        txt = self.font.render(self.text, True, text_color)
        screen.blit(txt, txt.get_rect(center=self.rect.center))


    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)






# --- UI Elements (initial) ---
start_btn   = Button((200, 350, 200, 50), 'Start', font_med, color=(100, 255, 255), hover_color=(50, 200, 255))
easy_btn    = Button((200, 300, 200, 40), 'Easy', font_small, color=(0, 255, 0), hover_color=(0, 250, 10))
med_btn     = Button((200, 350, 200, 40), 'Medium', font_small, color=(255, 215, 0), hover_color=(255, 180, 0))
hard_btn    = Button((200, 400, 200, 40), 'Hard', font_small, color=(255, 50, 50), hover_color=(255, 30, 30))
name_input  = TextInput((150,300,300,40))
next_btn    = Button((0, 0, 140, 40), 'Next', font_small, color=(100, 255, 255), hover_color=(50, 200, 255))
swap_btn    = Button((0, 0, 140, 40), 'Swap Tiles', font_small, color=(100, 255, 255), hover_color=(50, 200, 255))
pass_btn    = Button((0, 0, 140, 40), 'End Turn', font_small, color=(0, 255, 0), hover_color=(0, 250, 10))

bag_img = pygame.image.load('bag.png').convert_alpha()
bag_img = pygame.transform.scale(bag_img, (200,80))
swap_rect = bag_img.get_rect()

turn_img = pygame.image.load('turn.png').convert_alpha()
turn_img = pygame.transform.scale(turn_img,(200,80))
turn_rect = turn_img.get_rect()

# --- Game State --
state = 'start'
difficulty = None
player_name = ''
human_tiles = []
ai_tiles    = []
ai_name     = 'Ava'
human_score = ai_score = 0
ai_player   = QwirkleAI(name=ai_name, difficulty='hard', max_depth=3)




# --- Bag of Tiles (72) ---
colors = [c.lower() for c in COLORS.__dict__ if c.isupper()]
shapes = [s for k,s in SHAPES.__dict__.items() if k.isupper()]
bag    = [Piece(color, shape) for _ in range(2) for color in colors for shape in shapes]
random.shuffle(bag)




# --- Board & Drag State ---
board = Board(
    rows=GRID_SIZE,
    cols=GRID_SIZE,
    hex_spacing_x=HEX_SPACING_X,
    hex_height=HEX_HEIGHT,
    hex_radius=HEX_RADIUS,
    grid_x=GRID_X,
    grid_y=GRID_Y
)
dragging       = False
drag_tile      = None
mouse_x = mouse_y = 0
valid_moves    = []
selected_tile  = None
click_x = click_y = 0




def get_hand_tile_rect(idx, y_offset):
    # x0 is now the global HAND_X we set above
   
    return pygame.Rect(
       HAND_X + idx * (CELL_SIZE + TILE_GAP),
        y_offset,
        CELL_SIZE,
        CELL_SIZE
    )




# initial layout
update_layout()


falling_shapes = []  # Global list to store shapes


def squareanimation(dt):
    global falling_shapes
    if not falling_shapes:
        for _ in range(40):
            shape = {
                'x': random.randint(0, WINDOW_WIDTH - 30),
                'y': random.randint(-WINDOW_HEIGHT, WINDOW_HEIGHT),
                'size': random.randint(8, 30),
                'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                'shape': random.choice(['square', 'circle', 'triangle', 'star'])  # Add shape type
            }
            falling_shapes.append(shape)


    fall_speed = 30  # pixels per second


    for shape in falling_shapes:
        shape['y'] += fall_speed * dt


        # Reset to top
        if shape['y'] > WINDOW_HEIGHT:
            shape['y'] = random.randint(-100, -10)
            shape['x'] = random.randint(0, WINDOW_WIDTH - shape['size'])
            shape['shape'] = random.choice(['square', 'circle', 'triangle', 'star'])  # Optional reshuffle


        x = shape['x']
        y = int(shape['y'])
        s = shape['size']
        c = shape['color']
        t = shape['shape']


        if t == 'square':
            pygame.draw.rect(screen, c, (x, y, s, s))
        elif t == 'circle':
            pygame.draw.circle(screen, c, (x + s // 2, y + s // 2), s // 2)
        elif t == 'triangle':
            points = [(x + s // 2, y), (x, y + s), (x + s, y + s)]
            pygame.draw.polygon(screen, c, points)
        elif t == 'star':
            # Simple 5-point star approximation (static angles)
            cx, cy = x + s // 2, y + s // 2
            r = s // 2
            points = []
            for i in range(10):
                angle = math.radians(i * 36)
                radius = r if i % 2 == 0 else r // 2
                px = cx + int(math.cos(angle) * radius)
                py = cy + int(math.sin(angle) * radius)
                points.append((px, py))
            pygame.draw.polygon(screen, c, points)


# --- Main Loop ---
while True:
    dt = clock.tick(60) / 1000  # Convert milliseconds to seconds


    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif ev.type == pygame.USEREVENT:
             show_ai_message = False
             pygame.time.set_timer(pygame.USEREVENT, 0)
        elif ev.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = ev.w, ev.h
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            update_layout()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_f:
            toggle_fullscreen()




        # --- START SCREEN ---
        if state == 'start':
            if ev.type == pygame.MOUSEBUTTONDOWN and start_btn.is_clicked(ev.pos):
                state = 'name_difficulty'
       
        # --- DIFFICULTY SCREEN ---
        elif state == 'name_difficulty':
            name_input.handle_event(ev)
            
            if name_input.text:
                 easy_btn.draw(screen)
                 med_btn.draw(screen)
                 hard_btn.draw(screen)
       
            if ev.type == pygame.MOUSEBUTTONDOWN :
                if easy_btn.is_clicked(ev.pos):
                    difficulty = 'easy'
                elif med_btn.is_clicked(ev.pos):
                    difficulty = 'medium'
                elif hard_btn.is_clicked(ev.pos):
                    difficulty = 'hard'
                
            if ev.type == pygame.MOUSEBUTTONDOWN and next_btn.is_clicked(ev.pos):
                if name_input.text and difficulty:
                    player_name = name_input.text
                    
                    for _ in range(6):
                        if bag: human_tiles.append(bag.pop())
                        if bag: ai_tiles.append(bag.pop())
                    ai_player.set_tiles(ai_tiles)
                    state = 'game'  # Transition to game state
                    update_layout()  # Update the layout to match the new state

                
            




        # --- GAMEPLAY ---
       
       
        elif state == 'game':
            # --- Draw Swap & End Turn Buttons ONLY if in the game state ---
            
            screen.blit(bag_img, swap_rect)
            screen.blit(turn_img,turn_rect)
            
             



            if ev.type == pygame.MOUSEBUTTONDOWN:
                # 1) Swap Tiles — ends your turn immediately
    
                if swap_rect.collidepoint(ev.pos) and not in_turn:
                    ai_message = get_ai_comment()
                    show_ai_message = True
                    draw_ai_message(ai_message)  # Draw the message on the screen
                    pygame.display.flip()
                    pygame.time.set_timer(pygame.USEREVENT, 500)
                    bag.extend(human_tiles)
                    random.shuffle(bag)
                    human_tiles[:] = [bag.pop() for _ in range(6)]




                    # AI’s turn — animate each placement
                    board.start_turn()
                    while True:
                       
                        m = ai_player.choose_move(board)
                        if not m: break
                        r,c,i = m
                        try:
                            board.place_piece(r, c, ai_tiles[i])
                            ai_tiles.pop(i)
                            # redraw board instantly so user sees this move
                            for r in range(GRID_SIZE):
                                for c in range(GRID_SIZE):
                                    fill = HIGHLIGHT if (r, c) in valid_moves else PAGE_BG
                                    center_x, center_y = board.grid.get_hex_position(r, c)
                                    draw_hexagon_at(screen, cx,cy, HEX_RADIUS+3, PAGE_BG,neon)
                                    draw_hexagon_at(screen, cx,cy, HEX_RADIUS,HIGHLIGHT if (rr,cc) in valid_moves else PAGE_BG)


                                    # draw power-up icon
                                    pu = board.get_powerup_at(r, c)
                                    if pu and pu in powerup_icons:
                                        icon = powerup_icons[pu]
                                        screen.blit(icon, icon.get_rect(center=(center_x, center_y)))




                                    t = board.grid.get(r, c)
                                    if t:
                                        img = tiles_images.get((t.color.lower(), t.shape))
                                        if img:
                                            screen.blit(img, img.get_rect(center=(center_x, center_y)))


                            pygame.display.flip()
                            pygame.time.wait(500)
                        except InvalidMoveException:
                            break
                    ai_score += board.score_current_turn()
                    board.end_turn()
                    board.start_turn()  # ← Preserve AI’s move state


                    # refill racks
                    while len(human_tiles) < 6 and bag:
                        human_tiles.append(bag.pop())
                    while len(ai_tiles) < 6 and bag:
                        ai_tiles.append(bag.pop())
                    ai_player.set_tiles(ai_tiles)
                    in_turn = False
                    valid_moves = []
                    update_layout()
                    continue


                # 2) End Turn — commit your turn and animate AI
                if turn_rect.collidepoint(ev.pos) and in_turn:
                    ai_message = get_ai_comment()
                    show_ai_message = True
                    draw_ai_message(ai_message)
                    pygame.display.flip()
                    pygame.time.set_timer(pygame.USEREVENT, 500)
                    print("Timer set: 2000ms")
                    board.end_turn()
                    board.start_turn()
                    show_ai_message = False
                    while True:
                        m = ai_player.choose_move(board)
                        if not m: break
                        r,c,i = m
                        try:
                            board.place_piece(r, c, ai_tiles[i])
                            ai_tiles.pop(i)
                            # ✅ hex‐cell draw
                            for rr in range(GRID_SIZE):
                                for cc in range(GRID_SIZE):
                                    # white background for all AI redraws
                                    cx, cy = board.grid.get_hex_position(rr, cc)
                                    draw_hexagon_at(screen, cx,cy, HEX_RADIUS+3, PAGE_BG,neon)
                                    draw_hexagon_at(screen, cx,cy, HEX_RADIUS,HIGHLIGHT if (rr,cc) in valid_moves else PAGE_BG)


                                    # power‐up icon
                                    pu = board.get_powerup_at(rr, cc)
                                    if pu and pu in powerup_icons:
                                        icon = powerup_icons[pu]
                                        screen.blit(icon, icon.get_rect(center=(cx, cy)))


                                    # tile image
                                    t = board.grid.get(rr, cc)
                                    if t:
                                        img = tiles_images.get((t.color.lower(), t.shape))
                                        if img:
                                            screen.blit(img, img.get_rect(center=(cx, cy)))
                            pygame.display.flip()
                            pygame.time.wait(500)
        
                        except InvalidMoveException:
                            break
                    ai_score += board.score_current_turn()
                    board.end_turn()
                    board.start_turn()  # ← Preserve AI’s move state
                    # refill racks
                    while len(human_tiles) < 6 and bag:
                        human_tiles.append(bag.pop())
                    while len(ai_tiles) < 6 and bag:
                        ai_tiles.append(bag.pop())
                    ai_player.set_tiles(ai_tiles)
                    in_turn = False
                    valid_moves = []
                    update_layout()
                    continue
                elif ev.type == pygame.USEREVENT:
                    print("USEREVENT triggered")
                    show_ai_message = False  # Hide the AI message after the timer ends
                    pygame.time.set_timer(pygame.USEREVENT, 0) 
                
                # 3) Show Valid Moves on click
                for i in range(len(human_tiles)):
                    rect = get_hand_tile_rect(i, UI_Y+NAME_AREA_HEIGHT+10)
                    if rect.collidepoint(ev.pos):
                        selected_tile = (i, human_tiles[i])
                        click_x, click_y = ev.pos
                        valid_moves = board.get_valid_moves(human_tiles[i])
                        break


            elif ev.type == pygame.MOUSEMOTION and selected_tile:
                dx,dy = ev.pos[0]-click_x, ev.pos[1]-click_y
                if not dragging and (abs(dx)>5 or abs(dy)>5):
                    dragging = True; drag_tile = selected_tile
                if dragging:
                    mouse_x, mouse_y = ev.pos


            elif ev.type == pygame.MOUSEBUTTONUP and dragging and drag_tile:
                row, col = board.grid.pixel_to_hex(mouse_x, mouse_y)
                idx, tile = drag_tile
                if (row, col) in valid_moves:
                    if not in_turn:
                        board.start_turn()      # start YOUR turn once
                        in_turn = True
                    try:
                        pts = board.place_piece(row, col, tile)
                        human_tiles.pop(idx)
                        human_score += pts
                        
                    except InvalidMoveException:
                        invalid_move_sound.play()
                        board.reset_turn()
                        in_turn = False
                else:
                    invalid_move_sound.play()
                valid_moves = []
                dragging = False
                drag_tile = None
                selected_tile = None
                
            elif ev.type == pygame.USEREVENT:
                show_ai_message = False  # Hide the message after the timeout
                pygame.time.set_timer(pygame.USEREVENT, 0)


    # --- DRAW ---
    screen.fill((15, 23, 42))
    def render_text_with_border(font, text, text_color, border_color, border_width=2):
            base = font.render(text, True, text_color)
            size = base.get_size()
            border_surface = pygame.Surface((size[0] + border_width * 2, size[1] + border_width * 2), pygame.SRCALPHA)


            # Draw the border by rendering the text around the center in all directions
            for dx in range(-border_width, border_width + 1):
                for dy in range(-border_width, border_width + 1):
                    if dx != 0 or dy != 0:
                        border_surface.blit(font.render(text, True, border_color), (dx + border_width, dy + border_width))
           
            # Draw the main text in the center
            border_surface.blit(base, (border_width, border_width))
            return border_surface
    if state == 'start':
        squareanimation(dt)


        # Title Text with Border
        title_surface = render_text_with_border(font_large, 'Smart Qwirkle', (255, 255, 255), (0, 0, 0), border_width=3)
        padding = 30
        box_width = title_surface.get_width() + padding * 2
        box_height = title_surface.get_height() + padding
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = 100  # Moved up slightly to make more room below


        # Title Glow Box
        pygame.draw.rect(screen, (0, 255, 255), (box_x - 4, box_y - 4, box_width + 8, box_height + 8), border_radius=10)
        pygame.draw.rect(screen, (20, 20, 60), (box_x, box_y, box_width, box_height), border_radius=10)
        screen.blit(title_surface, (box_x + padding, box_y + padding // 2))


        # Rules Text
        rules_text = [
            "Welcome to Smart Qwirkle",
            "An AI-powered reinvention of the classic tile-matching game",
            "Smart Qwirkle challenges you to think strategically  ",
            "as you connect shapes and colors on a beautifully rendered hexagonal grid.",
            "Get ready to outthink, outplay, and outscore"
        ]
        rule_font = font_small


        rule_box_width = 900
        rule_box_height = len(rules_text) * 40 + 45
        rule_box_x = (WINDOW_WIDTH - rule_box_width) // 2
        rule_box_y = box_y + box_height + 30  # Now just below the title box


        # Glow Outline for Rules Box
        glow_rect = pygame.Rect(rule_box_x - 4, rule_box_y - 4, rule_box_width + 8, rule_box_height + 8)
        pygame.draw.rect(screen, (0, 255, 255), glow_rect, border_radius=15)
       
        # Inner Rules Box
        rule_box_rect = pygame.Rect(rule_box_x, rule_box_y, rule_box_width, rule_box_height)
        pygame.draw.rect(screen, (89, 15, 134), rule_box_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), rule_box_rect, 3, border_radius=15)


        # Centered Rules Text
        total_text_height = len(rules_text) * 36
        vertical_margin = (rule_box_height - total_text_height) // 2
        for i, line in enumerate(rules_text):
            rule_txt = rule_font.render(line, True, (255, 255, 255))
            rule_txt_rect = rule_txt.get_rect(center=(rule_box_rect.centerx, rule_box_rect.top + vertical_margin + (i * 45)))
            screen.blit(rule_txt, rule_txt_rect)


        # Start Button below rules box
        start_btn.rect.topleft = ((WINDOW_WIDTH - start_btn.rect.width) // 2, rule_box_rect.bottom + 30)
        start_btn.draw(screen)


    elif state=='name_difficulty':
        squareanimation(dt)
        label_txt = font_med.render('Enter Your Name:', True, (255, 255, 255))
        pad = 10
        lw, lh = label_txt.get_size()
        box_w = lw + pad * 2
        box_h = lh + pad
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = 100  # Adjust the Y position for your label

    # outer neon glow
        pygame.draw.rect(screen, (0, 255, 255), (box_x - 4, box_y - 4, box_w + 8, box_h + 8), border_radius=8)
        pygame.draw.rect(screen, (20, 20, 60), (box_x, box_y, box_w, box_h), border_radius=8)
        screen.blit(label_txt, (box_x + pad, box_y + pad // 2))

    # Position for name input field
        inp = name_input.rect
        inp.y = box_y + box_h + 40 
        glow_rect = pygame.Rect(inp.x - 4, inp.y - 4, inp.w + 4, inp.h + 8)
        pygame.draw.rect(screen, (0, 255, 255), glow_rect, border_radius=10)
        name_input.draw(screen, font_small)
        
        difficulty_label_txt = font_med.render('Select Difficulty:', True, (255, 255, 255))
        difficulty_label_box_w = difficulty_label_txt.get_width() + pad * 2
        difficulty_label_box_h = difficulty_label_txt.get_height() + pad
        difficulty_label_x = (WINDOW_WIDTH - difficulty_label_box_w) // 2
        difficulty_label_y = inp.bottom + 40  # Positioned below the name input field

    # Draw outer neon glow for the "Select Difficulty" label
        pygame.draw.rect(screen, (0, 255, 255), (difficulty_label_x - 4, difficulty_label_y - 4, difficulty_label_box_w + 8, difficulty_label_box_h + 8), border_radius=8)
        pygame.draw.rect(screen, (20, 20, 60), (difficulty_label_x, difficulty_label_y, difficulty_label_box_w, difficulty_label_box_h), border_radius=8)
        screen.blit(difficulty_label_txt, (difficulty_label_x + pad, difficulty_label_y + pad // 2))

    # Now position difficulty options below the name input
        gap = 20
        easy_btn.rect.topleft = ((WINDOW_WIDTH - easy_btn.rect.width) // 2, difficulty_label_y + difficulty_label_box_h +gap)
        med_btn.rect.topleft = ((WINDOW_WIDTH - med_btn.rect.width) // 2, easy_btn.rect.bottom + gap)
        hard_btn.rect.topleft = ((WINDOW_WIDTH - hard_btn.rect.width) // 2, med_btn.rect.bottom + gap)

        easy_btn.draw(screen)
        med_btn.draw(screen)
        hard_btn.draw(screen)
        
        if ev.type == pygame.MOUSEBUTTONDOWN:
         if easy_btn.is_clicked(ev.pos):
            difficulty = 'easy'
            easy_btn.selected = True
            med_btn.selected = False
            hard_btn.selected = False
            # Transition directly to game after selecting difficulty
            player_name = name_input.text  # Store player name
            for _ in range(6):
                if bag: human_tiles.append(bag.pop())
                if bag: ai_tiles.append(bag.pop())
            ai_player.set_tiles(ai_tiles)
            state = 'game'  # Transition to game state
            update_layout()  # Update the layout to match the new state
         elif med_btn.is_clicked(ev.pos):
            difficulty = 'medium'
            easy_btn.selected = False
            med_btn.selected = True
            hard_btn.selected = False
            # Transition directly to game after selecting difficulty
            player_name = name_input.text  # Store player name




        # board
    elif state == 'game':
        
         # --- DRAW BOARD WITH HEXAGONS ---  

        neon = (0,255,255)
        purple = (89,15,134)
        padding = 16
        rule_spacing = 8
        power_spacing = 4
        heading_gap = 16
        GOLD = (255, 215,   0)
        white       = (255,255,255)
        RED   = (255,  50,  50)
        GREEN = ( 50, 255,  50)


        rules = [
            "Rules:",
            "- Each player draws 6 tiles from the bag to \n  form their rack.",
            "- Match tiles by color or shape",
            "- Create columns or diagonals to score",
            "- Earn points by placing tiles strategically.",
            "- When the game ends,\n  Player with most points wins",
            "- You can Swap tiles from the bag.",
            "- You can replace as many tiles as you \n  are currently using.",
            "No duplicates \nA line can’t contain two tiles of the exact \nsame color + shape.",
            "Qwirkle bonus \nCompleting a line of six (all six shapes of \none color, or all six colors of one shape) \ngives you an extra +6 points."
        ]
        powerups = [
        (PowerUp.UNDO, "Delete opponent's last move"),
        (PowerUp.DOUBLE, "Double points on one tile"),
        ( PowerUp.WILD, "Place any tile"),
        ]
        box_w  = 425
        rules_height = font_med.get_height() + rule_spacing + len(rules[1:])*(font_small.get_height()+rule_spacing)
        pu_height    = font_med.get_height() + rule_spacing + len(powerups)*(CELL_SIZE*0.6 + rule_spacing)
        bottom_margin = box_y
        box_h = WINDOW_HEIGHT - box_y - bottom_margin

        box_x = WINDOW_WIDTH - box_w - 30
        box_y = GRID_Y

        # draw glow + inner
        glow_rect  = pygame.Rect(box_x-4, box_y-4, box_w+8, box_h+8)
        inner_rect = pygame.Rect(box_x,   box_y,   box_w,   box_h)
        pygame.draw.rect(screen, neon,   glow_rect,  border_radius=12)
        pygame.draw.rect(screen, purple, inner_rect, border_radius=12)

        y = box_y + padding

# — draw Rules heading centered —
        hdr = "Rules:"
        surf = font_med.render(hdr, True, GOLD)
        screen.blit(surf, (box_x + (box_w - surf.get_width())/2, y))
        y += surf.get_height() + rule_spacing

        for line in rules[1:]:
    # pick color
            if line.lower().startswith("no duplicates"):
              text_color = RED
            elif line.lower().startswith("qwirkle bonus"):
                text_color = GREEN
            else:
                text_color = white

    # split on any '\n'
            for subline in line.split("\n"):
                txt = font_small.render(subline, True, text_color)
                screen.blit(txt, (box_x + padding, y))
                y += txt.get_height() + rule_spacing

            
        y += heading_gap
        
        hdr = "Power-Ups:"
        surf = font_med.render(hdr, True, GOLD)
        screen.blit(surf, (box_x + (box_w - surf.get_width())/2, y))
        y += surf.get_height() + 2
        
        for pu_type, desc in powerups:
            icon = powerup_icons.get(pu_type)
            if icon:
        # scale icon if needed to match your font size
                ih = icon.get_height()
                screen.blit(icon, (box_x + padding, y))
                txt = font_small.render(desc, True, white)
        # vertically center text next to icon
                ty = y + (ih - txt.get_height())/2
                screen.blit(txt, (box_x + padding + icon.get_width() + 8, ty))
                y += ih + power_spacing
            else:
        # fallback if icon missing
                txt = font_small.render(desc, True, white)
                screen.blit(txt, (box_x + padding, y))
                y += txt.get_height() + power_spacing


        
        for rr in range(GRID_SIZE):
            for cc in range(GRID_SIZE):
                fill = HIGHLIGHT if (rr, cc) in valid_moves else PAGE_BG
                cx, cy = board.grid.get_hex_position(rr, cc)
                draw_hexagon_at(screen,
                            cx, cy,
                            HEX_RADIUS + 3,      # slightly larger radius
                            fill_color=PAGE_BG,  # just fill with bg so inside stays dark
                            outline_color=neon)
                draw_hexagon_at(screen, cx, cy, HEX_RADIUS, fill)


                # --- NEW: draw the grid coordinate text ---
                #coord_txt = font_small.render(f"{rr},{cc}", True, (0, 0, 0))
                #txt_rect = coord_txt.get_rect(center=(cx, cy))
                #screen.blit(coord_txt, txt_rect)
                pu = board.get_powerup_at(rr, cc)
                if pu in powerup_icons:
                    icon = powerup_icons[pu]
                    screen.blit(icon, icon.get_rect(center=(cx, cy)))
                tile = board.grid.get(rr, cc)
                if tile:
                    img = tiles_images.get((tile.color.lower(), tile.shape))
                    if img:
                     
                        screen.blit(img, img.get_rect(center=(cx, cy)))
    
        if show_ai_message:
            draw_ai_message(ai_message)

    # --- SCORES ---
    if state == 'game':
        padding = 8
        border = 4
        glow_radius = 8
        purple = (20, 20, 60)
        tile_gap = TILE_GAP
        rack_slots = len(human_tiles)
        rack_width = MAX_RACK_WIDTH
        rack_left = HAND_X
        rack_top = UI_Y + NAME_AREA_HEIGHT + 5
        margin_x = 50  # horizontal gap from rack
        margin_y = 20

    # --- New Combined Score Box ---
       # --- New Separate Score Boxes for AI and Human ---
        score_box_width = 250  # fixed width
        score_box_height = 120  # fixed height

        scores_x = 30
        scores_y = GRID_Y

    # AI Score Box
        ai_score_box = pygame.Rect(scores_x, GRID_Y , score_box_width, score_box_height)
        #ai_glow = ai_score_box.inflate(glow_radius, glow_radius)

    # Draw glow and AI score box
        #pygame.draw.rect(screen, neon, ai_glow, border_radius=12)
        #pygame.draw.rect(screen, purple, ai_score_box, border_radius=12)

    # Fir
    # st line: AI Score
        ai_heading = font_med.render("SCORE", True, (255, 255, 255))
        screen.blit(
            ai_heading,
            (ai_score_box.centerx - ai_heading.get_width() // 2,
            ai_score_box.y + padding)
        )

    # AI avatar + score
        y0 = ai_score_box.y + padding + ai_heading.get_height() + 5
        if ai_icon:
            screen.blit(ai_icon, (ai_score_box.x + padding, y0))
            text_x = ai_score_box.x + padding + ai_icon.get_width() + 8
            text_y = y0 + (ai_icon.get_height() - font_small.get_height()) // 2
        else:
            text_x = ai_score_box.x + padding
            text_y = y0
        ai_text = f'{ai_name}: {ai_score}'
        ai_surf = render_text_with_border(font_small, ai_text, (255, 255, 255), (0, 0, 0), border_width=2)
        screen.blit(ai_surf, (text_x, text_y))

    # Human Score Box (just below AI score box)
        human_score_box = pygame.Rect(30, WINDOW_HEIGHT - 400,250,120)
        #human_glow = human_score_box.inflate(glow_radius, glow_radius)

    # Draw glow and Human score box
        #pygame.draw.rect(screen, neon, human_glow, border_radius=12)
        #pygame.draw.rect(screen, purple, human_score_box, border_radius=12)

    # First line: Human Score
        human_heading = font_med.render("SCORE", True, (255, 255, 255))
        screen.blit(
            human_heading,
            (human_score_box.centerx - human_heading.get_width() // 2,
            human_score_box.y + padding)
        )

    # Human avatar + score
        y1 = human_score_box.y + padding + human_heading.get_height() + 5
        if human_icon:
            screen.blit(human_icon, (human_score_box.x + padding, y1))
            text_x = human_score_box.x + padding + human_icon.get_width() + 8
            text_y = y1 + (human_icon.get_height() - font_small.get_height()) // 2
        else:
            text_x = human_score_box.x + padding
            text_y = y1
        human_text = f'{player_name}: {human_score}'
        human_surf = render_text_with_border(font_small, human_text, (255, 255, 255), (0, 0, 0), border_width=2)
        screen.blit(human_surf, (text_x, text_y))




    # --- build ui_rects of exactly your swap, end-turn and hand tiles ---
        ui_rects = [swap_rect, turn_rect]
        ui_rects += [
            get_hand_tile_rect(i, UI_Y + NAME_AREA_HEIGHT + 10)
            for i in range(len(human_tiles))
        ]

    # --- compute tight bounds around those elements ---
        pad = 12
        min_x = min(r.left   for r in ui_rects)
        max_x = max(r.right  for r in ui_rects)
        min_y = min(r.top    for r in ui_rects)
        max_y = max(r.bottom for r in ui_rects)

        wrapper = pygame.Rect(
            min_x - pad,
            min_y - pad,
            (max_x - min_x) + pad*2,
            (max_y - min_y) + pad*2
        )

    # --- inflate outward (20px each side horizontally, 10px vertically) ---
        wrapper.inflate_ip(40, 20)

    # --- draw glow and border ---
        glow = wrapper.inflate(8, 8)
        pygame.draw.rect(screen, neon, glow,     border_radius=12, width=4)
        pygame.draw.rect(screen, neon, wrapper,  border_radius=12, width=2)
            




    # --- HAND ---  
    for i, t in enumerate(human_tiles):
        rect = get_hand_tile_rect(i, UI_Y + NAME_AREA_HEIGHT + 10)
        cx,cy = rect.center
        draw_hexagon_at(screen,cx,cy,  HEX_RADIUS,PAGE_BG,neon)
        img = tiles_images.get((t.color.lower(), t.shape))
        if img:
            screen.blit(img, img.get_rect(center=rect.center))
            


    # --- SWAP & END TURN BUTTONS ---
    screen.blit(bag_img, swap_rect)
    screen.blit(turn_img, turn_rect)


    # --- DRAG-PREVIEW ---
    if dragging and drag_tile:
        _, tile = drag_tile
        img = tiles_images.get((tile.color.lower(), tile.shape))
        if img:
            #ai_score_box = pygame.Rect(30, GRID_Y  , 250, 120)
            #ai_glow = ai_score_box.inflate(8, 8)  # Glow effect for the box

            #pygame.draw.rect(screen, neon, ai_glow, border_radius=12)
            #pygame.draw.rect(screen, (20, 20, 60), ai_score_box, border_radius=12)

    # AI Score Heading
            ai_heading = font_med.render("SCORE", True, (255, 255, 255))
            screen.blit(ai_heading, (ai_score_box.centerx - ai_heading.get_width() // 2, ai_score_box.y + 8))

    # AI avatar and score
            y0 = ai_score_box.y + 8 + ai_heading.get_height() + 5
            if ai_icon:
                screen.blit(ai_icon, (ai_score_box.x + 8, y0))
                text_x = ai_score_box.x + 8 + ai_icon.get_width() + 8
                text_y = y0 + (ai_icon.get_height() - font_small.get_height()) // 2
            else:
                text_x = ai_score_box.x + 8
                text_y = y0
            ai_text = f'{ai_name}: {ai_score}'
            ai_surf = render_text_with_border(font_small, ai_text, (255, 255, 255), (0, 0, 0), border_width=2)
            screen.blit(ai_surf, (text_x, text_y))

    # Draw Human score box (below AI score box)
            human_score_box = pygame.Rect( 30, WINDOW_HEIGHT- 400 ,250, 120)  # Adjusted Y position for Human score box
            #human_glow = human_score_box.inflate(8, 8)

            #pygame.draw.rect(screen, neon, human_glow, border_radius=12)
            #pygame.draw.rect(screen, (20, 20, 60), human_score_box, border_radius=12)

    # Human Score Heading
            human_heading = font_med.render("SCORE", True, (255, 255, 255))
            screen.blit(human_heading, (human_score_box.centerx - human_heading.get_width() // 2, human_score_box.y + 8))

    # Human avatar and score
            y1 = human_score_box.y + 8 + human_heading.get_height() + 5
            if human_icon:
                screen.blit(human_icon, (human_score_box.x + 8, y1))
                text_x = human_score_box.x + 8 + human_icon.get_width() + 8
                text_y = y1 + (human_icon.get_height() - font_small.get_height()) // 2
            else:
                text_x = human_score_box.x + 8
                text_y = y1
            human_text = f'{player_name}: {human_score}'
            human_surf = render_text_with_border(font_small, human_text, (255, 255, 255), (0, 0, 0), border_width=2)
            screen.blit(human_surf, (text_x, text_y))

        
        
        # hand
        for i,t in enumerate(human_tiles):
            rect = get_hand_tile_rect(i, UI_Y+NAME_AREA_HEIGHT+10)
            cx ,cy = rect.center
            draw_hexagon_at(screen,cx,cy,HEX_RADIUS,PAGE_BG,neon)
            img = tiles_images.get((t.color.lower(),t.shape))
            if img:
                screen.blit(img, img.get_rect(center=rect.center))


        # Swap & End‑turn buttons
        screen.blit(bag_img, swap_rect)
        screen.blit(turn_img, turn_rect)


        # drag‑preview
        if dragging and drag_tile:
            _,tile = drag_tile
            img = tiles_images.get((tile.color.lower(),tile.shape))
            if img:
                screen.blit(img, (mouse_x-CELL_SIZE//2, mouse_y-CELL_SIZE//2))
    pygame.display.flip()
    clock.tick(120)
