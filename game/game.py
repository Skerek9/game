import pygame
import sys
import os
import json
import random

pygame.init()

# Константы
WIDTH = HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
DARK_BLUE = (70, 120, 200)
GREEN = (0,255,0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
YELLOW = (255,255,0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("X vs. O")
pygame.display.set_icon(pygame.image.load('images/icon.bmp'))
clock = pygame.time.Clock()
FPS = 30

# Звук
pygame.mixer.music.load('soundtracks/General Release.mp3')
pygame.mixer.music.play(-1)
flPause = False  # глобальная переменная для паузы музыки

# Шрифты
font_big = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 30)


class Player:
    def __init__(self, username, password, wins=0, losses=0):
        self.username = username
        self.password = password
        self.wins = wins
        self.losses = losses
        self.winrate = self.calc_winrate()



    def calc_winrate(self):
        """Вычисляет процент побед"""
        total = self.wins + self.losses
        if total == 0:
            return 0
        return (self.wins / total) * 100

    def get_username(self):
        """Возвращает юзернейм"""
        return self.username

    def check_password(self, password):
        """Проверка правильности пароля"""
        return self.password == password

    def save(self, filename="players.json"):
        """Сохраняет (или обновляет) данные игрока в JSON файл"""
        player_data = {
            "username": self.username,
            "password": self.password,
            "wins": self.wins,
            "losses": self.losses,
            "winrate": self.winrate,
        }

        all_players = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    all_players = json.load(f)
                except json.JSONDecodeError:
                    all_players = []

        updated = False
        for i, p in enumerate(all_players):
            if p.get("username") == self.username:
                all_players[i] = player_data
                updated = True
                break

        if not updated:
            all_players.append(player_data)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_players, f, ensure_ascii=False, indent=4)

    @classmethod
    def get_by_username(cls, username, filename="players.json"):
        """Возвращает объект класса по юзернейму"""
        if not os.path.exists(filename):
            return None

        with open(filename, 'r', encoding='utf-8') as f:
            try:
                all_players = json.load(f)
            except json.JSONDecodeError:
                return None

        for data in all_players:
            if data.get("username") == username:
                return cls(
                    username=data["username"],
                    password=data["password"],
                    wins=data.get("wins", 0),
                    losses=data.get("losses", 0),
                    )
        return None

    @classmethod
    def exists(cls, username, filename="players.json"):
        """Проверка существования игрока с данным юзернеймом"""
        return cls.get_by_username(username, filename) is not None

    @classmethod
    def get_all(cls, filename="players.json"):
        """Возвращает список всех игроков"""
        if not os.path.exists(filename):
            return []
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                all_players = json.load(f)
            except json.JSONDecodeError:
                return []
        return [cls(
                username=p["username"],
                password=p["password"],
                wins=p.get("wins", 0),
                losses=p.get("losses", 0))
            for p in all_players]


class Button:
    """Кнопки"""
    def __init__(self, x, y, width, height, text, color, hover_color, image_path=''):
        self.rect = pygame.Rect(x, y, width, height)
        if image_path:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = None
            self.text = text
            self.color = color
            self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        """Рисует кнопку"""
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 3)
            text_surface = font_small.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Обработка действий"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class InputBox:
    """Поле ввода текста"""
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.active_color = YELLOW
        self.current_color = self.color
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = font_medium
        self.error_msg = ""

    def handle_event(self, event):
        """Обработка действий поля ввода"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.current_color = self.active_color
            else:
                self.active = False
                self.current_color = self.color
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.current_color = self.color
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20 and event.unicode.isprintable():
                    self.text += event.unicode
        return False

    def draw(self, screen):
        """Отображение опля ввода"""
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, self.current_color, self.rect, 3)
        if self.text:
            text_surface = self.font.render(self.text, True, BLACK)
        else:
            text_surface = self.font.render(self.placeholder, True, GRAY)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


        if self.error_msg:
            error_surface = font_small.render(self.error_msg, True, RED)
            error_rect = error_surface.get_rect(center=(self.rect.centerx, self.rect.bottom + 10))
            screen.blit(error_surface, error_rect)

    def get_text(self):
        """Получение введенного текста"""
        return self.text

    def set_error(self, msg):
        """Ошибка при вводе"""
        self.error_msg = msg

    def clear_error(self):
        """Удаление ошибки"""
        self.error_msg = ""


class Slider:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.volume = 0.5
        self.dragging = False
        self.slider_x = x + width * self.volume

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Проверяем нажатие на ползунок
            if abs(mouse_x - self.slider_x) < 10 and abs(mouse_y - self.rect.centery) < 10:
                self.dragging = True
            # Или клик по дорожке ползунка
            elif self.rect.collidepoint(mouse_x, mouse_y):
                self.slider_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
                self.volume = (self.slider_x - self.rect.x) / self.rect.width
                pygame.mixer.music.set_volume(self.volume)  # Для музыки

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                self.slider_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
                self.volume = (self.slider_x - self.rect.x) / self.rect.width
                pygame.mixer.music.set_volume(self.volume)


    def draw(self, screen):
        # Фон
        pygame.draw.rect(screen, GRAY, self.rect)
        # Заполненная часть
        fill_width = self.rect.width * self.volume
        pygame.draw.rect(screen, DARK_RED, (self.rect.x, self.rect.y, fill_width, self.rect.height))
        # Ползунок
        pygame.draw.circle(screen, BLACK, (int(self.slider_x), self.rect.centery), 10)
        # Обводка ползунка
        pygame.draw.circle(screen, DARK_RED, (int(self.slider_x), self.rect.centery), 10, 2)



class Game:
    def __init__(self):
        self.running = True
        self.state = "MENU"
        self.prev_state = self.state
        self.player = None
        self.error_message = ""

        # Параметры игры
        self.board_size = 3
        self.cell_size = HEIGHT // self.board_size
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = 'player'
        self.game_over = False
        self.winner = None


        # Кнопки/картинки
        center_x = WIDTH // 2
        # результаты
        self.scores_button = Button(center_x - 150, HEIGHT - 120,
                                    300, 50, "RECORDS", BLUE, DARK_BLUE)
        # лобби
        self.start_game_button = Button(center_x - 50, HEIGHT // 2 + 80,
                                        100, 50, "PLAY", RED, DARK_RED)
        self.lobby_icon = Button(center_x-120, center_x-200, 240, 260, '', '', '',
                                      image_path='images/lobby.bmp')
        # поле меню
        self.name_input = InputBox(center_x - 175, 150, 350, 50, "username")
        self.password_input = InputBox(center_x - 175, HEIGHT // 2 - 50, 350, 50, "password")
        self.start_button = Button(center_x - 100, HEIGHT // 2 + 20,
                                   200, 50, "START", BLUE, DARK_BLUE)
        # настройки
        self.settings_button = Button(WIDTH - 80, 10, 70, 70, '', '', '',
                                      image_path='images/settings_icon.bmp')
        self.switch_music_button = Button(100, 100, 150, 50, 'SOUND', BLUE, DARK_BLUE)
        self.music_input = InputBox(100, 170, 100, 50, "ID")
        self.slider = Slider(100, 50, 400, 20)


    # ---------------------- Отрисовка состояний ----------------------
    def draw_menu(self):
        screen.fill(BLACK)
        title_text = font_big.render("X vs. O", True, DARK_RED)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 70))
        screen.blit(title_text, title_rect)

        name_label = font_small.render("NAME:", True, WHITE)
        name_rect = name_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 175))
        screen.blit(name_label, name_rect)
        self.name_input.draw(screen)

        pass_label = font_small.render("LAST WORDS:", True, WHITE)
        pass_rect = pass_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        screen.blit(pass_label, pass_rect)
        self.password_input.draw(screen)

        self.start_button.draw(screen)
        self.settings_button.draw(screen)

        if self.error_message:
            err_surf = font_small.render(self.error_message, True, RED)
            err_rect = err_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(err_surf, err_rect)

        pygame.display.update()

    def draw_settings(self):
        screen.fill(BLACK)

        back_text = font_small.render("ESC - GO BACK", True, GRAY)
        screen.blit(back_text, (20, HEIGHT - 40))
        y = 100
        for _ in [f"ID    Soundtrack", "1      70K", "2      Before Every Load", "3      Blank Shell",
                  "4      General Release", "5      Monochrome LSD", "6      Socket Calibration",
                  "7      You are an Angel"]:
            soundtrack = font_small.render(_, True, GRAY)
            screen.blit(soundtrack, (WIDTH // 2, y))
            y += 50

        self.switch_music_button.draw(screen)
        self.music_input.draw(screen)
        self.slider.draw(screen)

        pygame.display.update()

    def draw_lobby(self):
        screen.fill(BLACK)
        self.settings_button.draw(screen)
        self.scores_button.draw(screen)

        if self.player:
            name_text = font_small.render(f"Player: {self.player.username}", True, WHITE)
            screen.blit(name_text, (10, 110))
            winrate_text = font_small.render(f"Luck: {self.player.winrate:.1f}%", True, WHITE)
            screen.blit(winrate_text, (10, 140))
            losses_text = font_small.render(f"Death count: {self.player.losses}", True, WHITE)
            screen.blit(losses_text, (10, 170))

        game_text = font_big.render("WIN OR DIE", True, DARK_RED)
        game_rect = game_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(game_text, game_rect)

        self.start_game_button.draw(screen)
        self.lobby_icon.draw(screen)

        back_text = font_small.render("ESC -Menu", True, GRAY)
        screen.blit(back_text, (20, HEIGHT - 40))
        pygame.display.update()

    def draw_scores(self):
        screen.fill(BLACK)
        title = font_medium.render("RECORDS", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)

        players = Player.get_all()
        players.sort(key=lambda p: p.winrate, reverse=True)

        y = 150
        for i, p in enumerate(players[:10], 1):
            text = f"{i}. {p.username}  WON: {p.wins} WINRATE: {p.winrate:.1f}%"
            surf = font_small.render(text, True, WHITE)
            rect = surf.get_rect(center = (WIDTH // 2, y))
            screen.blit(surf, rect)
            y += 40

        back_text = font_small.render("ESC - previous ", True, GRAY)
        screen.blit(back_text, (20, HEIGHT - 40))
        pygame.display.update()

    def draw_game(self):
        screen.fill(BLACK)

        # Рисуем сетку
        for x in range(1, self.board_size + 2):
            pygame.draw.line(screen, WHITE, (self.cell_size * x, 0),
                             (self.cell_size * x, HEIGHT), 3)
            pygame.draw.line(screen, WHITE, (0, self.cell_size * x),
                             (WIDTH, self.cell_size * x), 3)

        # Рисуем символы
        for row in range(self.board_size):
            for col in range(self.board_size):
                symbol = self.board[row][col]
                if symbol == 'X':
                    color = GREEN
                elif symbol == 'O':
                    color = RED
                else:
                    continue
                space = 15
                if symbol == 'X':
                    pygame.draw.line(screen, color,
                                     (col * self.cell_size + space, row * self.cell_size + space),
                                     (col * self.cell_size + self.cell_size - space,
                                      row * self.cell_size + self.cell_size - space), 15)
                    pygame.draw.line(screen, color,
                                     (col * self.cell_size + space, row * self.cell_size + self.cell_size - space),
                                     (col * self.cell_size + self.cell_size - space,
                                      row * self.cell_size + space), 15)
                elif symbol == 'O':

                    pygame.draw.circle(screen, color,
                                       (col * self.cell_size + self.cell_size // 2,
                                        row * self.cell_size + self.cell_size // 2),
                                       self.cell_size // 2 - space, 15)

        # Сообщение о победителе
        if self.game_over:
            if self.winner == "player":
                msg = "LUCKY YOU!"
                color = GREEN
            elif self.winner == "ai":
                msg = "YOU ARE DEAD!"
                color = RED
            else:
                msg = "DRAW!"
                color = WHITE
            win_text = font_big.render(msg, True, color,BLACK)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_text, win_rect)


        pygame.display.update()

    # ---------------------- Обработка событий ----------------------
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            enter_name = self.name_input.handle_event(event)
            enter_pass = self.password_input.handle_event(event)

            if self.start_button.handle_event(event) or enter_name or enter_pass:
                username = self.name_input.get_text()
                password = self.password_input.get_text()
                if not username or not password:
                    self.error_message = "Введите никнейм и пароль!"
                    self.name_input.set_error("")
                    self.password_input.set_error("")
                else:
                    if Player.exists(username):
                        p = Player.get_by_username(username)
                        if p and p.check_password(password):
                            self.player = p
                            self.error_message = ""
                            self.name_input.clear_error()
                            self.password_input.clear_error()
                            self.name_input.text = ""
                            self.password_input.text = ""
                            self.start_game()
                        else:
                            self.error_message = "Неверный пароль!"

                    else:
                        # Новый игрок
                        self.player = Player(username, password)
                        self.player.save()
                        self.error_message = ""
                        self.name_input.clear_error()
                        self.password_input.clear_error()
                        self.name_input.text = ""
                        self.password_input.text = ""
                        self.start_game()

            if self.settings_button.handle_event(event):
                self.prev_state = self.state
                self.state = "SETTINGS"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_lobby_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "MENU"
            if self.start_game_button.handle_event(event):
                self.start_game()
                self.state = "GAME"
            if self.scores_button.handle_event(event):
                self.prev_state = self.state
                self.state = "SCORES"
            if self.settings_button.handle_event(event):
                self.prev_state = self.state
                self.state = "SETTINGS"

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "LOBBY"

            if event.type == pygame.MOUSEBUTTONDOWN :
                # При нажатии лкм

                if self.game_over :
                    self.reset_game()
                    continue

                # Ход игрока

                if not self.game_over and self.turn == "player":
                    x, y = pygame.mouse.get_pos()
                    col = x // self.cell_size
                    row = y // self.cell_size

                    if self.make_move(row, col, "O"):
                        self.player_move(row,col)
                        self.check_game_over()

                        if not self.game_over and self.turn == "ai":

                            self.ai_move()
                            self.check_game_over()

    def handle_scores_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = self.prev_state

    def handle_settings_events(self):
        global flPause
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = self.prev_state

            enter_pressed = self.music_input.handle_event(event)

            if enter_pressed:
                music_id = self.music_input.get_text()
                if music_id.isdigit() and 1 <= int(music_id) <= 7:
                    music_folder = "./soundtracks"
                    files = os.listdir(music_folder)
                    idx = int(music_id) - 1
                    pygame.mixer.music.load(os.path.join(music_folder, files[idx]))
                    pygame.mixer.music.play(-1)

            if self.switch_music_button.handle_event(event):
                flPause = not flPause
                if flPause:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            self.slider.handle_event(event)



    # ---------------------- Логика игры ----------------------
    def make_move(self, row, col, symbol):
        """Определение хода"""
        if self.board[row][col] == "":
            self.board[row][col] = symbol
            self.turn = "ai" if symbol == 'O' else "player"
            return True
        return False

    def player_move(self,row, col):
        """Ход игрока"""
        empty = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                 if self.board[r][c] == ""]
        if empty:
            self.board[row][col] = "X"
            self.turn = "ai"

    def ai_move(self):
        """Ход ии"""
        empty = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                 if self.board[r][c] == ""]
        if empty:
            r, c = random.choice(empty)
            self.board[r][c] = "O"
            self.turn = "player"

    def check_game_over(self):
        for i in range(self.board_size):
            if all(self.board[i][j] == "X" for j in range(self.board_size)):
                self.game_over = True
                self.winner = "player"
                self.update_stats()
                return
            if all(self.board[i][j] == "O" for j in range(self.board_size)):
                self.game_over = True
                self.winner = "ai"
                self.update_stats()
                return
        for j in range(self.board_size):
            if all(self.board[i][j] == "X" for i in range(self.board_size)):
                self.game_over = True
                self.winner = "player"
                self.update_stats()
                return
            if all(self.board[i][j] == "O" for i in range(self.board_size)):
                self.game_over = True
                self.winner = "ai"
                self.update_stats()
                return
        if all(self.board[i][i] == "X" for i in range(self.board_size)):
            self.game_over = True
            self.winner = "player"
            self.update_stats()
            return
        if all(self.board[i][i] == "O" for i in range(self.board_size)):
            self.game_over = True
            self.winner = "ai"
            self.update_stats()
            return
        if all(self.board[i][self.board_size - 1 - i] == "X" for i in range(self.board_size)):
            self.game_over = True
            self.winner = "player"
            self.update_stats()
            return
        if all(self.board[i][self.board_size - 1 - i] == "O" for i in range(self.board_size)):
            self.game_over = True
            self.winner = "ai"
            self.update_stats()
            return

        # Проверка на ничью
        if all(self.board[i][j] != "" for i in range(self.board_size) for j in range(self.board_size)):
            self.game_over = True
            self.winner = "tie"
            self.update_stats()

    def update_stats(self):
        if not self.player:
            return
        if self.winner == "player":
            self.player.wins += 1
        elif self.winner == "ai":
            self.player.losses += 1
        # при ничьей ничего не меняем
        self.player.winrate = self.player.calc_winrate()
        self.player.save()

    def reset_game(self):
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = "player"
        self.game_over = False
        self.winner = None


    def start_game(self):
        self.reset_game()
        self.state = "LOBBY"

    # ---------------------- Основной цикл ----------------------
    def run(self):
        while self.running:
            if self.state == "MENU":
                self.handle_menu_events()
                self.draw_menu()
            elif self.state == "LOBBY":
                self.handle_lobby_events()
                self.draw_lobby()
            elif self.state == "SETTINGS":
                self.handle_settings_events()
                self.draw_settings()
            elif self.state == "GAME":
                self.handle_game_events()
                self.draw_game()
            elif self.state == "SCORES":
                self.handle_scores_events()
                self.draw_scores()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


