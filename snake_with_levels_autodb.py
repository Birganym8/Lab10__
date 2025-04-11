import sqlite3

def init_db():
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        level INTEGER,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
    ''')

    conn.commit()
    conn.close()

init_db()


import pygame, sys, random, sqlite3
from pygame.math import Vector2

# ---------- DATABASE SETUP ----------
def get_user_data(username):
    conn = sqlite3.connect('snake_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        cursor.execute("SELECT score, level FROM user_score WHERE user_id = ?", (user_id,))
        score_data = cursor.fetchone()
        conn.close()
        return user_id, score_data if score_data else (0, 1)
    else:
        cursor.execute("INSERT INTO user (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id, (0, 1)

def save_state(user_id, score, level):
    conn = sqlite3.connect('snake_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_score WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute("UPDATE user_score SET score = ?, level = ? WHERE user_id = ?", (score, level, user_id))
    else:
        cursor.execute("INSERT INTO user_score (user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
    conn.commit()
    conn.close()

def calculate_level(score):
    if score < 10:
        return 1
    elif score < 20:
        return 2
    else:
        return 3

def calculate_speed(level):
    if level == 1:
        return 200
    elif level == 2:
        return 150
    else:
        return 100

# ---------- USER LOGIN ----------
username = input("Enter your username: ")
user_id, (saved_score, saved_level) = get_user_data(username)

# ---------- SNAKE CLASS ----------
class SNAKE:
    def __init__(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(0,0)
        self.new_block = False
        self.crunch_sound = pygame.mixer.Sound('Sound/crunch.wav')
    def draw_snake(self):
        for block in self.body:
            x = int(block.x * cell_size)
            y = int(block.y * cell_size)
            block_rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, (0,100,0), block_rect)
    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
    def add_block(self):
        self.new_block = True
    def play_crunch_sound(self):
        self.crunch_sound.play()
    def reset(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(0,0)

# ---------- FRUIT CLASS ----------
class FRUIT:
    def __init__(self):
        self.randomize()
    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        pygame.draw.rect(screen, (255,0,0), fruit_rect)
    def randomize(self):
        self.pos = Vector2(random.randint(0, cell_number - 1), random.randint(0, cell_number - 1))
        self.type = random.choice(["apple", "banana", "grape"])

# ---------- MAIN CLASS ----------
class MAIN:
    def __init__(self, saved_score=0, saved_level=1):
        self.snake = SNAKE()
        self.fruit = FRUIT()
        self.score = saved_score
        self.level = saved_level
    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
    def draw_elements(self):
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()
    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            if self.fruit.type == "banana":
                self.score += 2
            elif self.fruit.type == "grape":
                self.score += 5
            else:
                self.score += 1
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
            new_level = calculate_level(self.score)
            if new_level != self.level:
                self.level = new_level
                pygame.time.set_timer(SCREEN_UPDATE, calculate_speed(self.level))
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
    def check_fail(self):
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            self.game_over()
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()
    def game_over(self):
        self.snake.reset()
        self.score = 0
        self.level = 1
        pygame.time.set_timer(SCREEN_UPDATE, calculate_speed(self.level))
    def draw_score(self):
        score_surface = game_font.render(f'Score: {self.score} | Level: {self.level}', True, (0, 0, 0))
        screen.blit(score_surface, (10, 10))

# ---------- GAME SETUP ----------
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
cell_size = 30
cell_number = 20
screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
clock = pygame.time.Clock()
game_font = pygame.font.SysFont("Arial", 25)

main_game = MAIN(saved_score, saved_level)
current_level = calculate_level(saved_score)
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, calculate_speed(current_level))

is_paused = False

# ---------- GAME LOOP ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE and not is_paused:
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and main_game.snake.direction.y != 1:
                main_game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and main_game.snake.direction.y != -1:
                main_game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and main_game.snake.direction.x != 1:
                main_game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and main_game.snake.direction.x != -1:
                main_game.snake.direction = Vector2(1, 0)
            if event.key == pygame.K_p:
                is_paused = not is_paused
                if is_paused:
                    save_state(user_id, main_game.score, main_game.level)

    screen.fill((175, 215, 70))
    if not is_paused:
        main_game.draw_elements()
    else:
        pause_surface = game_font.render("Paused. Press P to resume.", True, (0, 0, 0))
        screen.blit(pause_surface, (cell_size, cell_size * cell_number // 2))
    pygame.display.update()
    clock.tick(60)
