import pygame
import config
import sausage
import player
import os
import random

EDIBLE_IMAGE = pygame.image.load(os.path.join("Assets",config.EDIBLE))
NON_EDIBLE_IMAGE = pygame.image.load(os.path.join("Assets",config.NON_EDIBLE))
CHARACTER_IMAGE = pygame.image.load(os.path.join("Assets",config.CHARACTER))
BACKGROUND_IMAGE = pygame.image.load(os.path.join("Assets",config.BACKGROUND))
HEART_IMAGE = pygame.image.load(os.path.join("Assets",config.HEART))

CHARACTER_IMAGE = pygame.transform.scale(CHARACTER_IMAGE,(config.CHAR_W,config.CHAR_H))
EDIBLE_IMAGE = pygame.transform.scale(EDIBLE_IMAGE,(config.FOOD_SIZE,config.FOOD_SIZE))
NON_EDIBLE_IMAGE = pygame.transform.scale(NON_EDIBLE_IMAGE,(config.FOOD_SIZE,config.FOOD_SIZE))
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (config.WIDTH,config.HEIGHT))
HEART_IMAGE = pygame.transform.scale(HEART_IMAGE, (40,40))

pygame.mixer.init()
NON_EDIBLE_SOUND = pygame.mixer.Sound(os.path.join("Assets",config.NON_EDIBLE_SOUND))
HIT_SOUND = pygame.mixer.Sound(os.path.join("Assets",config.HIT_SOUND))
LOST_SOUND = pygame.mixer.Sound(os.path.join("Assets",config.LOST_SOUND))

class State:
    def __init__(self,edible_img,non_edible_img,heart_img,non_edible_sound,hit_sound,player,font):
        self.score = 0
        self.obj = list()
        self.lives = config.LIVES
        self.spawn_direction = "L"
        self.edible_img = edible_img
        self.non_edible_img = non_edible_img
        self.heart_img = heart_img
        self.non_edible_sound = non_edible_sound
        self.hit_sound = hit_sound
        self.player = player
        self.font = font
        self.alpha_non_edible = 0
        self.life_portion = 1

    def spawn_obj(self):
        if self.if_spawn():
            if random.random() < config.PROBABILITY_NON_EDIBLE:
                spawn_edible = False
                image = self.non_edible_img
            else:
                spawn_edible = True
                image = self.edible_img

            if not self.obj:
                x = int(random.randrange(0,config.WIDTH-config.FOOD_SIZE))
            else:
                last_obj_x=self.obj[len(self.obj)-1].x_1
                self.update_spawn_direction()
                if self.spawn_direction == "L":
                    x = last_obj_x-config.FOOD_SIZE
                else:
                    x = last_obj_x+config.FOOD_SIZE
            new_sausage = sausage.Sausage(x,0,spawn_edible,image)
            self.obj.append(new_sausage)

    def update_spawn_direction(self):
        last_obj = self.obj[len(self.obj) - 1]
        jerk = (random.random() < config.PROBABILITY_JERK)

        if jerk:
            if self.spawn_direction == "L":
                self.spawn_direction = "R"
            else:
                self.spawn_direction = "L"

        if last_obj.x_1-config.FOOD_SIZE<0:
            self.spawn_direction = "R"
        elif last_obj.x_2+config.FOOD_SIZE>config.WIDTH:
            self.spawn_direction = "L"

    def handle_jitter(self,id):
        dir = random.choice([-1,1])
        new_x = self.obj[id].x_1+dir*config.JITTER_MAGNITUDE
        if dir > 0 and new_x+config.FOOD_SIZE<config.WIDTH:
            self.obj[id].x_1= new_x
            self.obj[id].x_2 = new_x + config.FOOD_SIZE
        elif dir < 0 and new_x > 0:
            self.obj[id].x_1= new_x
            self.obj[id].x_2 = new_x + config.FOOD_SIZE

    def obj_update_position(self):
        for id,object in enumerate(self.obj):
            object.y_1 += config.FALL_SPEED
            object.y_2 += config.FALL_SPEED
            if config.FALL_JITTER and random.random() < config.FALL_JITTER_PROBABILITY:
                self.handle_jitter(id)

    def update(self, mx, my, click):
        self.obj_update_position()
        self.detect_collisions(mx,my,click)
        self.spawn_obj()

    def if_spawn(self):
        if self.obj:
            last_obj_y = self.obj[len(self.obj)-1].y_1
            if last_obj_y-config.FOOD_SIZE < 0:
                return False
            else:
                return random.random()<config.CHANCE_SPAWN
        return True

    def detect_collisions(self,mx,my,click):
        collision_detected = False
        for id,object in enumerate(self.obj):
            y_bottom_obj = object.y_2
            y_at_most = self.player.y + int(config.LATE_CATCH_ALLOWANCE*config.FOOD_SIZE)
            if y_bottom_obj >= self.player.y and y_bottom_obj <= y_at_most:
                if object.x_1>=self.player.x and object.x_2<=self.player.x_2:
                    collision_detected = True
                    self.handle_non_edible_col(id)
                    self.obj.pop(id)
            elif click and (mx >= object.x_1 and mx <= object.x_2) and (my <= object.y_2 and my >= object.y_1):
                collision_detected = True
                self.handle_non_edible_col(id)
                self.obj.pop(id)

        self.handle_health_increment(collision_detected)

    def handle_health_increment(self,collision):
        if collision:
            self.life_portion = min(1,self.life_portion+config.LIFE_INCREASE_RATE)
        else:
            self.life_portion = max(0,self.life_portion-config.LIFE_DECREASE_RATE)
        if self.life_portion == 0:
            self.lives -= 1
            self.life_portion = 1

    def handle_non_edible_col(self,id):
        if self.obj[id].edible == False:
            self.alpha_non_edible = config.ALPHA_NON_EDIBLE
            self.score = max(0,self.score-config.SCORE_DECREASE)
            self.non_edible_sound.play()
        else:
            self.alpha_non_edible = max(self.alpha_non_edible-1,0)
            self.score += config.SCORE_INCREASE
            self.hit_sound.play()

    def update_score(self):
        return self.font.render('Score: {}'.format(self.score), False, (0, 0, 0))

    def draw_life_bar(self,screen):
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(0, 0, config.WIDTH*self.life_portion, 10))

def draw_quotes(quotes):
    font = pygame.font.SysFont("helveticaneue", 15)
    text_surf = font.render(quotes, True, (255, 255, 255))
    text_surf.set_alpha(120)
    return text_surf

def draw_window(screen,current_game,quotes):
    screen.blit(BACKGROUND_IMAGE,(0,0))
    screen.blit(current_game.player.image,(current_game.player.x,current_game.player.y))
    for object in current_game.obj:
        screen.blit(object.image, (object.x_1,object.y_1))
    green_layer = pygame.Surface((config.WIDTH, config.HEIGHT))  # the size of your rect
    green_layer.set_alpha(current_game.alpha_non_edible)  # alpha level
    green_layer.fill((154,205,50))  # this fills the entire surface
    screen.blit(green_layer, (0, 0))  # (0,0) are the top-left coordinates

    for i in range(current_game.lives):
        screen.blit(current_game.heart_img,(i*41,20))

    current_game.draw_life_bar(screen)
    screen.blit(draw_quotes(quotes),(0,config.HEIGHT-20))
    screen.blit(current_game.update_score(),(3,68))
    pygame.display.update()

def update_quotes(quotes):
    return quotes[1:]

def generate_quotes():
    lines = []
    with open(os.path.join("Assets",config.QUOTES)) as f:
        for l in f.readlines():
            if l[0].isdigit():
                l = l.split()
                l = l[1:]
                lines.append(l)
    quotes = list()
    for q in lines:
        quote = " ".join(q)
        quotes.append(quote)
    random.shuffle(quotes)
    quote_str = ""
    for q in quotes:
        quote_str += (q+"  ")
    return quote_str

def start_screen(screen):
    running = True
    clock = pygame.time.Clock()
    frame_count = 0
    font_size = 15
    digit = 3
    alpha = 120
    font_2 = pygame.font.SysFont("helveticaneue", 30)
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while digit>0:
            font = pygame.font.SysFont("helveticaneue", font_size)
            clock.tick(config.FPS_LIMIT)
            if (frame_count % 1) == 0 and font_size < 100:
                font_size += 4
            elif font_size >= 100:
                alpha -= 1

            if alpha <= 0:
                font_size = 2
                alpha = 100
                digit -= 1
            else:
                text_surf = font.render(str(digit), False, (255, 255, 255))
                text_surf.set_alpha(alpha)
                centerTitle = text_surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT//2))

            screen.blit(BACKGROUND_IMAGE, (0, 0))
            screen.blit(text_surf, centerTitle)

            text_surf_2 = font_2.render("Get ready to get your ass flabbergasted! :-)", False, (255, 255, 255))
            centerTitle_2 = text_surf_2.get_rect(center=(config.WIDTH // 2, config.HEIGHT - 80 ))
            screen.blit(text_surf_2, centerTitle_2)

            pygame.display.update()
            frame_count += 1
        running = False
    game(screen)

def game(screen):
    clock = pygame.time.Clock()
    BACKGROUND_SONG = pygame.mixer.music.load(os.path.join("Assets", config.SONG))
    pygame.mixer.music.play(-1)
    running = True
    frame_count = 0
    char = player.Player(config.WIDTH//2,config.HEIGHT-config.CHAR_H,CHARACTER_IMAGE)
    font = pygame.font.SysFont("Arial", 25)
    current_game = State(EDIBLE_IMAGE,NON_EDIBLE_IMAGE,HEART_IMAGE,NON_EDIBLE_SOUND,HIT_SOUND,char,font)
    quotes = generate_quotes()

    while running:
        clock.tick(config.FPS_LIMIT)
        draw_window(screen,current_game,quotes)

        mx, my = pygame.mouse.get_pos()
        click = False

        if (frame_count % 7) == 0:
            quotes = update_quotes(quotes)
            if not quotes:
                quotes = generate_quotes()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        keys_pressed = pygame.key.get_pressed()
        char.handle_movement(keys_pressed)

        current_game.update(mx,my,click)

        if current_game.lives == 0:
            pygame.mixer.music.stop()
            game_over(screen,current_game.score)
            running = False
        frame_count+=1

def game_over(screen,score):
    def strike(text):
        return ''.join([u'\u0336{}'.format(c) for c in text])

    LOST_SONG = pygame.mixer.music.load(os.path.join("Assets", config.LOST_SOUND))
    pygame.mixer.music.play(-1)

    running = True
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("helveticaneue", 30)

    while running:
        clock.tick(config.FPS_LIMIT)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.mixer.music.stop()
                    start_screen(screen)
                if event.key == pygame.K_q:
                    running = False

        text_surf = font.render("You lost! Your ching chong {} is {}".format((strike("credit") + " score"),
                                                                score),False, (255, 255, 255))
        text_surf_2 =  font.render("Press F to {} start a new game and Q to quit outta here".format(strike("pay respect")),
                                   False, (255, 255, 255))
        text_surf.set_alpha(200)
        text_surf_2.set_alpha(200)
        centerTitle = text_surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 + 50))
        centerTitle_2 = text_surf_2.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50))
        screen.blit(text_surf, centerTitle)
        screen.blit(text_surf_2,centerTitle_2)
        pygame.display.update()

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode([config.WIDTH,config.HEIGHT])
    pygame.display.set_caption('Günters adventure in Wuhan')
    start_screen(screen)

if __name__=="__main__":
    main()