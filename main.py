import pygame
import random
import sys

# 初始化
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("飞机大战")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 时钟
clock = pygame.time.Clock()
FPS = 60

# 字体
font = pygame.font.SysFont("simhei", 24)  # 中文字体
big_font = pygame.font.SysFont("simhei", 48)

# 加载图片（如果没有图片文件，会用彩色矩形代替）
def load_image(color, size):
    """创建纯色矩形作为替代图片"""
    surf = pygame.Surface(size)
    surf.fill(color)
    return surf

# 玩家飞机类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image(GREEN, (50, 60))
        # 绘制飞机形状
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (50, 60), (25, 45), (0, 60)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 5
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # 边界限制
        self.rect.clamp_ip(screen.get_rect())

        # 无敌时间
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 120  # 2秒无敌
            self.rect.centerx = SCREEN_WIDTH // 2
            self.rect.bottom = SCREEN_HEIGHT - 20
            return True
        return False

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image(YELLOW, (4, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -8

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# 敌机类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 50)
        self.image = load_image(RED, (size, size))
        # 绘制敌机形状
        pygame.draw.polygon(self.image, RED, [(size//2, size), (0, 0), (size, 0)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)
        self.score = 10

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# 爆炸效果类
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        for i in range(5):
            size = 20 + i * 10
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 200 - i*30, 0), (size//2, size//2), size//2)
            self.frames.append(surf)
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]
                self.rect = self.image.get_rect(center=self.rect.center)

# 游戏主函数
def main():
    # 精灵组
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    # 创建玩家
    player = Player()
    all_sprites.add(player)

    score = 0
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60  # 初始生成间隔
    game_over = False
    victory = False

    running = True
    while running:
        clock.tick(FPS)

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                elif event.key == pygame.K_r and game_over:
                    # 重新开始
                    return main()
                elif event.key == pygame.K_q and game_over:
                    running = False

        if not game_over:
            # 生成敌机
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = 0
                # 随着分数增加，敌机生成加快
                enemy_spawn_delay = max(20, 60 - score // 100)

            # 更新
            all_sprites.update()

            # 子弹击中敌机
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += hit.score
                explosion = Explosion(hit.rect.centerx, hit.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

            # 敌机撞击玩家
            if not player.invincible:
                hits = pygame.sprite.spritecollide(player, enemies, True)
                if hits:
                    for hit in hits:
                        explosion = Explosion(hit.rect.centerx, hit.rect.centery)
                        all_sprites.add(explosion)
                        explosions.add(explosion)
                    if player.hit():
                        if player.lives <= 0:
                            game_over = True

            # 敌机漏掉（到达底部）不扣血，但可能影响评价

        # 绘制
        screen.fill(BLACK)

        # 绘制星空背景
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)

        all_sprites.draw(screen)

        # 绘制分数和生命
        score_text = font.render(f"分数: {score}", True, WHITE)
        lives_text = font.render(f"生命: {player.lives}", True, GREEN)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        # 无敌闪烁效果
        if player.invincible and player.invincible_timer % 10 < 5:
            pygame.draw.circle(screen, YELLOW, player.rect.center, 35, 2)

        # 游戏结束画面
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            over_text = big_font.render("游戏结束", True, RED)
            final_score = font.render(f"最终分数: {score}", True, WHITE)
            restart_text = font.render("按 R 重新开始", True, GREEN)
            quit_text = font.render("按 Q 退出", True, WHITE)

            screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, 250))
            screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, 320))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 380))
            screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 420))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
