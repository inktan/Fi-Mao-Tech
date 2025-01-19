import pygame

class Snake(pygame.sprite.Sprite):
    #定义构造函数
    def __init__(self,filename,location):
        # 调父类来初始化子类
        pygame.sprite.Sprite.__init__(self)
        # 加载图片
        self.image = pygame.image.load(filename)
        # 获取图片rect区域
        self.rect = self.image.get_rect()
        # 设置位置
        self.rect.topleft=location

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((500,400))
pygame.display.set_caption('C语言中文网')
# 填充为白色屏幕
screen.fill((255,255,255))
filename ="C:/Users/Administrator/Desktop/snake.png"

location =(100,150)
snake1 = Snake(filename,location)
# 碰撞检测,必须有两个精灵，因此再创建一个精灵，并使用location来控制第二个精灵的位置
location_2 = (100,80)
snake2 = Snake('C:/Users/Administrator/Desktop/logo.png',location_2)
# 调用 collide_rect()进行矩形区域检测，返回一个布尔值，碰撞返回True，否则返回False
crash_result = pygame.sprite.collide_rect(snake1,snake2)
if crash_result:
    print("精灵碰撞了!")
    pass
else:
    print('精灵没碰撞')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # 绘制精灵到屏幕上
    screen.blit(snake1.image,snake1.rect)
    screen.blit(snake2.image,snake2.rect)
    # 刷新显示屏幕
    pygame.display.update()