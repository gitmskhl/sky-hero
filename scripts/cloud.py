from random import randint, choice
from scripts.utils import load_images, load_image
from scripts.physics import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK

class Cloud:
    loaded = False

    def init_images():
        Cloud.img = load_image('images/clouds/cloud_1.png', 1)
        Cloud.images = load_images('images/clouds', SCREEN_WIDTH / (Cloud.img.get_width() * 10), BLACK)
        Cloud.free_zone = SCREEN_WIDTH // 20
        Cloud.loaded = True
    
    def __init__(self):
        if not Cloud.loaded:
            Cloud.init_images()
        self.image = choice(Cloud.images)    
        self.x = randint(-Cloud.free_zone, SCREEN_WIDTH + Cloud.free_zone)
        self.y = randint(-Cloud.free_zone, SCREEN_HEIGHT + Cloud.free_zone)
        self.speed = randint(1, 100) / 500

    def update(self, shifts):
        self.x += self.speed
        cloud_x = self.x - shifts[0]
        cloud_y = self.y - shifts[1]
        if cloud_x < -Cloud.free_zone:
            cloud_x = SCREEN_WIDTH + Cloud.free_zone
        elif cloud_x > SCREEN_WIDTH + Cloud.free_zone:
            cloud_x = -Cloud.free_zone
        if cloud_y < -Cloud.free_zone:
            cloud_y = SCREEN_HEIGHT + Cloud.free_zone
        elif cloud_y > SCREEN_HEIGHT + Cloud.free_zone:
            cloud_y = -Cloud.free_zone
        self.x = cloud_x + shifts[0]
        self.y = cloud_y + shifts[1]
        
    
    def render(self, screen, shifts):
        cloud_x = self.x - shifts[0]
        cloud_y = self.y - shifts[1]
        screen.blit(self.image, (cloud_x, cloud_y))



class Clouds:
    def __init__(self, count=20):
        self.clouds = [Cloud() for _ in range(count)]
        self.shifts = [0, 0]
        self.camera = None
    
    def update(self, camera):
        coef = 10
        if self.camera:
            self.shifts[0] += (camera[0] - self.camera[0]) / coef
            self.shifts[1] += (camera[1] - self.camera[1]) / coef
        self.camera = list(camera)
        for cloud in self.clouds:
            cloud.update(self.shifts)
    
    def render(self, screen):
        for cloud in self.clouds:
            cloud.render(screen, self.shifts)
                


