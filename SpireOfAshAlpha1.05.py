import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 20
ENEMY_SIZE = 20
ITEM_SIZE = 15
FPS = 60

# Player constants
DEFAULT_SPEED = 5
MAX_HEALTH = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)  # Explosion color
BLUE = (0, 0, 255)  # Attack area color
GREEN = (0, 255, 0)  # Door color
PINK = (255, 192, 203)  # Health item
PURPLE = (128, 0, 128)  # Attack power item
ORANGE = (255, 165, 0)  # Speed item

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Roguelike Game with Advanced Features")
clock = pygame.time.Clock()

# Font for score and health display
font = pygame.font.Font(None, 36)

# Helper function to display text
def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

#Main Menu Function
def main_menu():
    title_font = pygame.font.Font(None, 74)
    prompt_font = pygame.font.Font(None, 36)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        screen.fill(BLUE)

        # Draw title
        title_surface = title_font.render("Spire of Ash", True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_surface, title_rect)

        # Draw prompt
        prompt_surface = prompt_font.render("Press spacebar to start!", True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = DEFAULT_SPEED
        self.health = MAX_HEALTH
        self.attack_power = 1

    def move(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def attack(self, enemies, keys):
        if keys[pygame.K_UP]:
            attack_area = pygame.Rect(self.rect.x, self.rect.y - PLAYER_SIZE * 3, PLAYER_SIZE, PLAYER_SIZE * 3)
        elif keys[pygame.K_DOWN]:
            attack_area = pygame.Rect(self.rect.x, self.rect.y + PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE * 3)
        elif keys[pygame.K_LEFT]:
            attack_area = pygame.Rect(self.rect.x - PLAYER_SIZE * 3, self.rect.y, PLAYER_SIZE * 3, PLAYER_SIZE)
        elif keys[pygame.K_RIGHT]:
            attack_area = pygame.Rect(self.rect.x + PLAYER_SIZE, self.rect.y, PLAYER_SIZE * 3, PLAYER_SIZE)
        else:
            attack_area = pygame.Rect(self.rect.x - PLAYER_SIZE * 1.5, self.rect.y - PLAYER_SIZE * 1.5, PLAYER_SIZE * 3, PLAYER_SIZE * 3)

        pygame.draw.rect(screen, BLUE, attack_area, 2)
        enemies_removed = 0
        for enemy in enemies:
            if attack_area.colliderect(enemy.rect):
                enemies.remove(enemy)
                enemies_removed += self.attack_power
        return enemies_removed

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2
        self.attack_cooldown = 1000
        self.last_attack_time = pygame.time.get_ticks()

    def move_toward_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed

        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

    def can_attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = now
            return True
        return False

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.rect = pygame.Rect(x, y, ITEM_SIZE, ITEM_SIZE)
        self.item_type = item_type
        self.color = PINK if item_type == "health" else PURPLE if item_type == "attack" else ORANGE

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.rect.centerx, self.rect.centery), ITEM_SIZE // 2)

def generate_random_room(player_spawn_x, player_spawn_y):
    enemies = pygame.sprite.Group()
    items = pygame.sprite.Group()
    for _ in range(random.randint(3, 10)):
        while True:
            x = random.randint(0, WIDTH - ENEMY_SIZE)
            y = random.randint(0, HEIGHT - ENEMY_SIZE)
            if ((x - player_spawn_x) ** 2 + (y - player_spawn_y) ** 2) ** 0.5 > 50:
                enemies.add(Enemy(x, y))
                break
    for _ in range(random.randint(1, 3)):
        x = random.randint(0, WIDTH - ITEM_SIZE)
        y = random.randint(0, HEIGHT - ITEM_SIZE)
        item_type = random.choice(["health", "attack", "speed"])
        items.add(Item(x, y, item_type))
    return enemies, items

def explode(x, y):
    for i in range(5):
        pygame.draw.circle(screen, YELLOW, (x + PLAYER_SIZE // 2, y + PLAYER_SIZE // 2), i * 5)
        pygame.display.flip()
        pygame.time.delay(50)

# Main game loop
def main():
    player = Player(WIDTH // 2, HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    enemies, items = generate_random_room(player.rect.x, player.rect.y)

    score = 0
    door_open = False

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)

        if keys[pygame.K_SPACE]:
            score += player.attack(enemies, keys)

        for enemy in enemies:
            enemy.move_toward_player(player)
            if enemy.rect.colliderect(player.rect) and enemy.can_attack():
                player.health -= 1
                if player.health <= 0:
                    explode(player.rect.x, player.rect.y)
                    player.rect.x, player.rect.y = WIDTH // 2, HEIGHT // 2
                    main_menu()
                    enemies, items = generate_random_room(player.rect.x, player.rect.y)
                    score = 0
                    player.health = MAX_HEALTH
                    door_open = False
                    break

        if len(enemies) == 0:
            door_open = True

        for item in items:
            if player.rect.colliderect(item.rect):
                if item.item_type == "health" and player.health < MAX_HEALTH:
                    player.health += 1
                elif item.item_type == "attack":
                    player.attack_power = 2
                elif item.item_type == "speed":
                    player.speed = 8
                items.remove(item)

        if door_open:
            pygame.draw.rect(screen, GREEN, (WIDTH - 50, HEIGHT // 2 - 50, 40, 100))

        if door_open and player.rect.right >= WIDTH - 50 and HEIGHT // 2 - 50 < player.rect.centery < HEIGHT // 2 + 50:
            player.rect.x, player.rect.y = WIDTH // 2, HEIGHT // 2
            enemies, items = generate_random_room(player.rect.x, player.rect.y)
            door_open = False

        all_sprites.update()
        enemies.update()
        all_sprites.draw(screen)
        enemies.draw(screen)

        for item in items:
            item.draw()

        draw_text(f"Score: {score}", WHITE, WIDTH - 150, 10)
        draw_text(f"Health: {player.health}", WHITE, 10, 10)
        draw_text("Items: Pink=Health, Purple=Attack, Orange=Speed", WHITE, 10, HEIGHT - 30)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main_menu()
    main()
