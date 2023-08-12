import os
import sys
import pygame
import math
import Styling

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_image(filename):
    """loads an image, prepares it for play"""
    file = resource_path(os.path.join("assets", filename))
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit(f'Could not load image "{file}" {pygame.get_error()}')
    return surface.convert()

class Base(pygame.sprite.Sprite):
    def __init__(self):
        self.visible = False
        pygame.sprite.Sprite.__init__(self)

    def setVisibility(self, visible):
        self.visible = visible

    def isVisible(self):
        return self.visible

class Timer(Base):
    def __init__(self):
        Base.__init__(self)
        self.time = 0
        self.time_limit = 20

    def updateData(self, delta_t):
        if self.isVisible():
            self.time = delta_t

    def update(self, screen):
        if self.isVisible():
            font = pygame.font.Font('freesansbold.ttf', 20)
            text = font.render(str(round(self.time, 1)), True, Styling.Colors.Black)
            text_rect = text.get_rect()
            text_rect.topleft = (50, 50)
            text_box = pygame.draw.rect(screen, Styling.Colors.Red, text_rect.inflate(10, 10), 5)
            screen.blit(text, text_rect)
    
    def reset(self):
        self.__init__()

class Obstacle(Base):
    def __init__(self, cord = [0,0], move_speed = 0, rotate = 0):
        Base.__init__(self)
        self.cord = cord
        self.image = pygame.transform.scale(load_image("enemy.gif").convert(), (50,22))
        self.image = pygame.transform.rotate(self.image, rotate)
        self.explode_image = pygame.transform.rotate(pygame.transform.scale(load_image("slipper.gif"), (30,52)),90)
        self.rect = self.image.get_rect(midbottom=self.cord)
        self.move_speed = move_speed
        self.rotate = rotate

    def reset(self):
        self.__init__(self.cord, self.move_speed)

    def update(self, screen, screen_size):
        if self.isVisible():
            if self.rotate > 0:
                self.cord[0] += self.move_speed
                if self.cord[0]>screen_size[0] or self.cord[0]<0:
                    self.move_speed = -self.move_speed
            else:
                self.cord[1] += self.move_speed
                if self.cord[1]>screen_size[1] or self.cord[1]<0:
                    self.move_speed = -self.move_speed
            self.rect = self.image.get_rect(center=self.cord)
            screen.blit(self.image, self.rect)
    
    def collision_check(self, object, screen):
        if self.isVisible():
            if self.rect.colliderect(object.rect):
                self.setVisibility(False)
                explosion_rect = self.explode_image.get_rect()
                explosion_rect.center = self.cord
                screen.blit(self.explode_image, explosion_rect)
                return True
        return False

class Tower(Base):
    def __init__(self, cord = [0,0], move = False):
        Base.__init__(self)
        self.cord = cord
        self.tower1 = pygame.transform.rotate(pygame.transform.scale(load_image("slipper.gif").convert(), (60,104)),15)
        self.tower1_rect = self.tower1.get_rect(midtop=self.cord)
        self.tower2 = pygame.transform.rotate(self.tower1, -50)
        self.tower2_rect = self.tower2.get_rect(topright=self.cord)
        self.tower2_rect = self.tower2_rect.move((self.tower1_rect.midtop[0]-self.tower2_rect.midtop[0])/2,0)
        self.tower3 = pygame.transform.flip(self.tower2, True, False)
        self.tower3_rect = self.tower3.get_rect(topleft=self.cord)
        self.tower3_rect = self.tower3_rect.move((self.tower1_rect.midtop[0]-self.tower3_rect.midtop[0])/2,0)
        self.explode_image = pygame.transform.rotate(pygame.transform.scale(load_image("slipper.gif"), (60,104)),90)
        self.move = move
        self.move_speed = 5

    def reset(self):
        self.__init__(self.cord, self.move)

    def update(self, screen):
        if self.isVisible():
            screen.blit(self.tower3, self.tower3_rect)
            screen.blit(self.tower2, self.tower2_rect)
            screen.blit(self.tower1, self.tower1_rect)

    
    def collision_check(self, object, screen):
        if self.isVisible():
            if self.tower1_rect.colliderect(object.rect):
                explosion_rect = self.explode_image.get_rect()
                explosion_rect.center = self.cord
                screen.blit(self.explode_image, explosion_rect)
                return True
        return False
class AngleLine(Base):
    def __init__(self, screen_size):
        Base.__init__(self)
        self.angle = math.radians(45)
        self.length = 100
        self.screen_size = screen_size
        self.startPos = [10, screen_size[1]-10]
        self.endPos = [self.startPos[0] + self.length, self.startPos[1]]
        self.thickness = 5

    def setAngle(self, angle):
        self.angle = angle
    
    def getAngle(self):
        return self.angle

    def getAngleDegree(self):
        return math.degrees(self.angle)

    def calculateAngle(self, userInput):
        newAngle = math.degrees(self.angle) + userInput
        if newAngle > 90:
            newAngle = 89
        if newAngle <= 0:
            newAngle = 1
        self.setAngle(math.radians(newAngle))

    def getEndPos(self):
        return self.endPos
    
    def setEndPos(self, newPos):
        self.endPos = newPos

    def calculateEndPos(self):
        x = self.length * math.cos(self.angle)
        y = self.length * math.sin(self.angle)
        newPos = [x + self.startPos[0], self.startPos[1]-y]
        self.setEndPos(newPos)

    def draw(self, screen):
        circles = 7
        x_list = []
        y_list = []
        x_list.append(self.startPos[0])
        y_list.append(self.startPos[1])
        for i in range(1, circles):
            x_list.append(self.startPos[0] + ((self.endPos[0]-self.startPos[0])/circles)*i)
        for i in range(1, circles):
            y_list.append(self.startPos[1] + ((self.endPos[1]-self.startPos[1])/circles)*i)
        x_list.append(self.endPos[0])
        y_list.append(self.endPos[1])
        for i in range(circles):
            pygame.draw.circle(screen, Styling.Colors.Black, [x_list[i], y_list[i]],self.thickness + 1)
            pygame.draw.circle(screen, Styling.Colors.Yellow, [x_list[i], y_list[i]],self.thickness)

    def update(self, screen):
        if self.isVisible():
            self.draw(screen)

    def updateData(self):
        if self.isVisible():
            self.calculateEndPos()
    
    def reset(self):
        self.__init__(self.screen_size)

class PowerBar(Base):
    def __init__(self, screen_size):
        Base.__init__(self)
        self.lowerLimit = 10
        self.screen_size = screen_size
        self.upperLimit = 600
        self.thickness = 10
        self.length = self.lowerLimit
        self.startPos = [150, screen_size[1]-50]
        self.upperLeftPos = [self.startPos[0], self.startPos[1] + self.thickness]
        self.endPos = [self.startPos[0] + self.length, self.startPos[1]]
        self.upperRightPos = [self.endPos[0],self.endPos[1] + self.thickness]
        self.powerSpeed = 5
        self.shapeSequence = [self.startPos, self.upperLeftPos, self.upperRightPos, self.endPos]

    def getLength(self):
        return self.length

    def setLength(self):
        self.length += self.powerSpeed
        if self.length > self.upperLimit:
            self.length = self.upperLimit
            self.powerSpeed = -self.powerSpeed
        if self.length < self.lowerLimit:
            self.length = self.lowerLimit
            self.powerSpeed = -self.powerSpeed

    def getStartPos(self):
        return self.startPos

    def getUpperLeft(self):
        return self.upperLeftPos
    
    def getEndPos(self):
        return self.endPos
        
    def setEndPos(self):
        newCord = [self.startPos[0] + self.getLength(), self.startPos[1]]
        self.endPos = newCord

    def setUpperRight(self):
        self.upperRightPos = [self.endPos[0],self.endPos[1] + self.thickness]

    def getUpperRight(self):
        return self.upperRightPos

    def getShapeSequence(self):
        return self.shapeSequence

    def setShapeSequence(self):
        self.shapeSequence = [self.getStartPos(), self.getUpperLeft(), self.getUpperRight(), self.getEndPos()]

    def draw(self, screen):
        pygame.draw.polygon(screen, Styling.Colors.Red, self.getShapeSequence(), width=0)
        #enclosing box
        coverSequence = [[self.startPos[0] - 1, self.startPos[1] - 1], [self.startPos[0] -1, self.upperLeftPos[1]+1], [self.upperLeftPos[0] + self.upperLimit + 1,self.upperLeftPos[1]+1], [self.upperLeftPos[0] + self.upperLimit + 1, self.startPos[1] - 1]]
        pygame.draw.polygon(screen, Styling.Colors.Black, coverSequence, 5)

    def update(self, screen):
        if self.isVisible():
            self.draw(screen)

    def updateData(self):
        if self.isVisible():
            self.setLength()
            self.setEndPos()
            self.setUpperRight()
            self.setShapeSequence()

    def reset(self):      
        self.__init__(self.screen_size)

class Selipar(Base):
    def __init__(self):
        Base.__init__(self)
        self.cord = [10, 10]
        self.image = pygame.transform.scale(load_image("slipper.gif"), (45,69))
        self.rect = self.image.get_rect(center=self.cord)
        self.spin_angle = 0
        self.spinned_image = self.image
        self.spinned_image_rect = self.rect

    def get_cord(self):
        return self.cord
        
    def calculate_x(self, v, theta, delta_t):
        return  math.floor(v*math.cos(theta)*delta_t)

    def calculate_y(self, cur_x, theta, v, delta_t, gravity, screen_size):
        part1 = cur_x*math.tan(theta)
        cos2 = (1+math.cos(theta*2))/2
        if cos2 == 0:
            return screen_size[1]-(v*delta_t-gravity*delta_t*delta_t/2)
        else:
            part2 = gravity*cur_x*cur_x/2/v/v/cos2
            return screen_size[1]-math.floor(part1-part2)
    
    def calculate_new_cord(self, v, theta, delta_t, gravity, screen_size):
        new_x = self.calculate_x(v, theta, delta_t)
        new_y = self.calculate_y(new_x, theta, v, delta_t, gravity, screen_size)
        self.cord = [new_x, new_y]

    def spin(self):
        #https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        self.spinned_image = pygame.transform.rotate(self.image, self.spin_angle)
        #Currently the optimal spin yang tak nampak pelik sangat
        spin_increment = 10
        self.spin_angle+=spin_increment
        if self.spin_angle > 360:
            self.spin_angle = 0

    def update(self, screen):
        if self.isVisible():
            screen.blit(self.spinned_image, self.spinned_image_rect)

    def updateData(self, v, theta, delta_t, gravity, screen_size):
        if self.isVisible():
            self.spin()
            self.calculate_new_cord(v, theta, delta_t, gravity, screen_size)
            self.rect.center = self.cord
            self.spinned_image_rect.center = self.cord

    def reset(self):
        self.__init__()

class Player(Base):
    def __init__(self):
        Base.__init__(self)
        self.cord = [10, 700]
        self.image = load_image("player.gif")#pygame.transform.scale(load_image("player.gif"), (30,52))
        self.rect = self.image.get_rect(center=self.cord)
        self.angle = 0
        self.spinned_image = self.image
        self.spinned_image_rect = self.rect
        self.speed = 2

    def getAngleDegree(self):
        return math.degrees(self.angle)

    def calculateAngle(self, userInput1, userInput2):
        self.angle = self.angle + self.speed*userInput1 + self.speed*userInput2

    def spin(self):
        #https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        self.spinned_image = pygame.transform.rotate(self.image, self.angle)

    def move(self, userInput, screen_size):
        new_x = self.cord[0] + self.speed*userInput[0]
        new_y = self.cord[1] + self.speed*userInput[1]
        if new_x < 0:
            self.rect.left = 0
            new_x = self.rect.center[0]
        if new_x > screen_size[0]:
            self.rect.right = screen_size[0]
            new_x = self.rect.center[0]
        if new_y <0:
            self.rect.top = 0
            new_y = self.rect.center[1]
        if new_y > screen_size[1]:
            self.rect.bottom = screen_size[1]
            new_y = self.rect.center[1]
        self.cord = [new_x, new_y]

    def update(self, screen):
        if self.isVisible():
            screen.blit(self.spinned_image, self.spinned_image_rect)

    def updateData(self):
        if self.isVisible():
            self.spin()
            self.rect.center = self.cord
            self.spinned_image_rect.center = self.cord
    
    def reset(self):
        self.__init__()

class Bullet(Base):
    def __init__(self, player):
        Base.__init__(self)
        self.cord = player.cord
        self.image = pygame.transform.scale(load_image("slipper.gif"), (30,52))
        self.rect = self.image.get_rect(center=self.cord)
        self.angle = player.angle
        self.v = 20
        self.dx = 0
        self.dy = 0
        self.spinned_image = self.image
        self.spinned_image_rect = self.rect
        self.spin_angle = 0
        self.shot = False

    def spin(self):
        #https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        self.spinned_image = pygame.transform.rotate(self.image, self.spin_angle)
        #Currently the optimal spin yang tak nampak pelik sangat
        spin_increment = 30
        self.spin_angle+=spin_increment
        if self.spin_angle > 360:
            self.spin_angle = 0

    def set_dy_dx(self):
        self.dx = self.v * math.cos(math.radians(-self.angle))
        self.dy = self.v * math.sin(math.radians(-self.angle))
    
    def set_shot_state(self, shot_state):
        self.shot = shot_state
    
    def is_shot(self):
        return self.shot
    
    def move(self):
        self.cord = [self.cord[0] + self.dx, self.cord[1] + self.dy]

    def update(self, player, screen, screen_size):
        if self.isVisible():
            self.shot = True
            self.spin()
            self.move()
            self.rect.center = self.cord
            self.spinned_image_rect.center = self.cord
            screen.blit(self.spinned_image, self.spinned_image_rect)
        if self.cord[0] < 0 or self.cord[0] > screen_size[0] or self.cord[1] < 0 or self.cord[1] > screen_size[1]:
            self.setVisibility(False)
            self.cord = player.cord     
            self.shot = False      

class Menu(Base):
    def __init__(self, screen_size, padding = 10):
        Base.__init__(self)
        self.cord = [0, 0]
        self.base_rect = pygame.Rect.inflate(pygame.Rect(0, screen_size[1], screen_size[0], screen_size[1]),-screen_size[0]/10, -screen_size[1]/6)
        self.base_rect.center = [screen_size[0]/2, screen_size[1]/2]
        self.cover_rect = pygame.Rect.inflate(self.base_rect, padding, padding)

        self.title_font_size = 72
        self.title_font = pygame.font.SysFont(None, self.title_font_size)
        self.title_text = 'Malay Traditional Game: Baling Selipar'
        self.title_text_image = self.title_font.render(self.title_text, True, Styling.Colors.Black)
        self.title_text_rect = self.title_text_image.get_rect()
        self.title_text_rect.midtop = [self.base_rect.midtop[0], self.base_rect.midtop[1] + self.title_font_size]

        self.text_font_size = 48
        self.text_font = pygame.font.SysFont(None, 24)
        self.text_list = []
        self.text_list.append('Baling Selipar is a Malaysian traditional game.')
        self.text_list.append('The game requires two teams which are the  defender and the attacker.')
        self.text_list.append('Before the start of the game, the defender will build a pyramid made of three flipflops.')
        self.text_list.append('The attacker group will then attempt to destroy the pyramid by throwing a flipflop from a distance.')
        self.text_list.append('Once the pyramid is destroyed, the defender group will attempt to rebuild the pyramid.')
        self.text_list.append('The attacker must stop the defender group from rebuilding the pyramid by eliminating the')
        self.text_list.append('defenders by attacking them with flipflops')
        self.text_list.append('Players will be in the attacking group that are trying to destroy the flip flop pyramid.')
        self.text_list.append('The path to victory is only a flipflop throw away.')
        self.text_list.append('')
        self.text_list.append('Press ''ENTER'' to start the game.')

        self.text_image_list = list()
        self.text_rect_list = list()
        for i in range(len(self.text_list)):
            self.text_image_list.append(self.text_font.render(self.text_list[i], True, Styling.Colors.Black))
            self.text_rect_list.append(self.text_image_list[i].get_rect(midtop = [self.title_text_rect.midtop[0], self.title_text_rect.midtop[1] + self.title_font_size + self.text_font_size*i]))
        self.setVisibility(True)
    
    def update(self, screen):
        if self.isVisible():
            pygame.draw.rect(screen, Styling.Colors.Black, self.cover_rect, 0, 10)
            pygame.draw.rect(screen, Styling.Colors.White, self.base_rect, 0, 10)
            screen.blit(self.title_text_image, self.title_text_rect)
            for i in range(len(self.text_list)):
                screen.blit(self.text_image_list[i] , self.text_rect_list[i])

class Dialog(Base):
    def __init__(self, screen_size, padding = 10, text = f'Stage: ', number = 1):
        Base.__init__(self)
        self.cord = [0, 0]
        self.base_rect = pygame.Rect.inflate(pygame.Rect(0, screen_size[1], screen_size[0], screen_size[1]),-screen_size[0]/2, -screen_size[1]/1.4)
        self.base_rect.center = [screen_size[0]/2, screen_size[1]/2]
        self.cover_rect = pygame.Rect.inflate(self.base_rect, padding, padding)

        self.title_font_size = 72
        self.title_font = pygame.font.SysFont(None, self.title_font_size)
        self.title_text = f'{text}{number}'
        self.title_text_image = self.title_font.render(self.title_text, True, Styling.Colors.Black)
        self.title_text_rect = self.title_text_image.get_rect()
        self.title_text_rect.midtop = [self.base_rect.midtop[0], self.base_rect.midtop[1] + self.title_font_size]

        self.text_font_size = 48
        self.text_font = pygame.font.SysFont(None, 24)
        self.text_list = [f'Press ''SPACEBAR'' to start.']
        self.text_image_list = list()
        self.text_rect_list = list()
        for i in range(len(self.text_list)):
            self.text_image_list.append(self.text_font.render(self.text_list[i], True, Styling.Colors.Black))
            self.text_rect_list.append(self.text_image_list[i].get_rect(midtop = [self.title_text_rect.midtop[0], self.title_text_rect.midtop[1] + self.title_font_size + self.text_font_size*i]))
    
    def update(self, screen):
        if self.isVisible():
            pygame.draw.rect(screen, Styling.Colors.Black, self.cover_rect, 0, 10)
            pygame.draw.rect(screen, Styling.Colors.White, self.base_rect, 0, 10)
            screen.blit(self.title_text_image, self.title_text_rect)
            for i in range(len(self.text_list)):
                screen.blit(self.text_image_list[i] , self.text_rect_list[i])

class HelpDialog(Base):
    def __init__(self, screen_size, section_title, text_list, padding = 10):
        Base.__init__(self)
        self.cord = [0, 0]
        self.base_rect = pygame.Rect(0, 200, 400, 200)
        self.base_rect.topright = [screen_size[0]-padding, padding]
        self.cover_rect = pygame.Rect.inflate(self.base_rect, padding, padding)

        self.title_font_size = 48
        self.title_font = pygame.font.SysFont(None, self.title_font_size)
        self.title_text = section_title
        self.title_text_image = self.title_font.render(self.title_text, True, Styling.Colors.Black)
        self.title_text_rect = self.title_text_image.get_rect()
        self.title_text_rect.midtop = [self.base_rect.midtop[0], self.base_rect.midtop[1] + self.title_font_size]

        self.text_font_size = 24
        self.text_font = pygame.font.SysFont(None, 24)
        self.text_list = text_list
        self.text_image_list = list()
        self.text_rect_list = list()
        for i in range(len(self.text_list)):
            self.text_image_list.append(self.text_font.render(self.text_list[i], True, Styling.Colors.Black))
            self.text_rect_list.append(self.text_image_list[i].get_rect(midtop = [self.title_text_rect.midtop[0], self.title_text_rect.midtop[1] + self.title_font_size + self.text_font_size*i]))
    
    def update(self, screen):
        if self.isVisible():
            pygame.draw.rect(screen, Styling.Colors.Black, self.cover_rect, 0, 10)
            pygame.draw.rect(screen, Styling.Colors.White, self.base_rect, 0, 10)
            screen.blit(self.title_text_image, self.title_text_rect)
            for i in range(len(self.text_list)):
                screen.blit(self.text_image_list[i] , self.text_rect_list[i])



