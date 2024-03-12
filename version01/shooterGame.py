import pygame as pg
import random
from math import *
from os import path

# All constants required

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
TITLE = "Cosmic Cataclysm"
FPS = 60
IMG_DIR = path.join(path.dirname(__file__), "assets") # Directory to assets folder that we will always use
FONT_NAME = pg.font.match_font("BatmanForeverAlternate")# Font name

# Color Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SUPER_DARK_GREY = (15, 15, 15)
DARK_GREY = (30, 30, 30)
MODERATE_GREY = (49, 49, 49)
LIGHT_GREY = (126, 126, 126)
RED = (255, 0, 0)
LIGHT_GREEN = (70, 255, 51)
GREEN = (5, 107, 0)
BLUE = (0, 143, 230)
LIGHT_BLUE = (0, 255, 255)
PURPLE = (138, 1, 206)
YELLOW = (255, 255, 0)


class Player(pg.sprite.Sprite): # Player class based on the pre-defined pygame sprite class
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.dir = pg.image.load(path.join(IMG_DIR, "playerShip2_blue.png")).convert()
        self.originalImage = pg.transform.scale(self.dir, (75, 57))# Image directory
        self.originalImage.set_colorkey(BLACK)
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect() # Get the hitbox of the player
        self.radius = 30 # Circle collisions must have an attribute called self.radius
        self.shooting = False

        '''Properties in game'''
        self.rect.centerx = SCREEN_WIDTH / 4 # Starting x position
        self.rect.centery = SCREEN_HEIGHT - 75 # Starting y position
        self.speedx = 0 # The player is stationary at default
        self.speedy = 0
        self.angle = 0
        self.lastShot = (pg.time.get_ticks() / 1000) # Get the time when the player has last shot
        self.firerate = 0.5 # In seconds
        self.level = 1
        self.maxExp = int(round2(50 * exp2((self.level - 1)/5))) # Defaulted to 50
        self.currentEXP = 0
        self.maxHP = floor(100 * exp((self.level - 1)/50)) # Defaulted to 100
        self.currentHP = self.maxHP
        self.damage = 2
        self.cash = 100 # Default cash starts at 100

    def update(self):
        '''Update player state'''
        self.rotate()
        self.speedx = 0 # Reset the speed
        self.speedy = 0
        keyState = pg.key.get_pressed() # Obtains a list of every key on the keyboard and whether the key is up or down
        mouseState = pg.mouse.get_pressed() # Obtains a list of the left and right mouse and whether the mouse button is up or down
        mouseLocation = pg.mouse.get_pos()
        if keyState[pg.K_LEFT] or keyState[pg.K_a]:
            self.speedx -= 5
        if keyState[pg.K_RIGHT] or keyState[pg.K_d]:
            self.speedx += 5
        if keyState[pg.K_UP] or keyState[pg.K_w]:
            self.speedy += 5
        if keyState[pg.K_DOWN] or keyState[pg.K_s]:
            self.speedy -= 5
        # Check for diagonal elements
        if self.speedx != 0 and self.speedy != 0:
            angle = radians(45)
            self.speedx *= cos(angle) # Horizontal components
            self.speedy *= sin(angle) # Vertical components
        # Mouse handlers for shooting mechanics
        if mouseState[0] and mouseLocation[0] <= 600:
            self.shoot()

        self.rect.x += self.speedx # Move the rect
        self.rect.y -= self.speedy # Directions are reversed in the y axis
        # Check if the rect touches the edges
        if self.rect.right > (SCREEN_WIDTH // 2) - 20:
            self.rect.right = (SCREEN_WIDTH // 2) - 20
        if self.rect.left < 20:
            self.rect.left = 20
        if self.rect.top < 20:
            self.rect.top = 20
        if self.rect.bottom > (SCREEN_HEIGHT - 20):
            self.rect.bottom = (SCREEN_HEIGHT - 20)
    
    def rotate(self):
        '''Method that rotates the player sprite based on the direction of the mouse pointer'''
        mouseLocation = pg.mouse.get_pos()
        horizontal = mouseLocation[0] - self.rect.centerx
        vertical = mouseLocation[1] - self.rect.centery
        # Pygame's coordinate system has x-coordinates pointing to the right and y-coordinates pointing downwards. The 180 degrees prevent this from happening.
        self.angle = (degrees(atan2(horizontal, vertical)) + 180)
        self.image = pg.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect(center = self.rect.center)
    
    def shoot(self):
        '''Shooting mechanics'''
        currentTime = (pg.time.get_ticks() / 1000) # Get current time
        if currentTime - self.lastShot > self.firerate: # If the the space button is held, fire in 0.5s intervals
            self.lastShot = currentTime # Update the last shot to the current time when a shot is fired
            bullet = PlayerBullet(self.rect.centerx, self.rect.centery, self.angle)
            self.game.allSprites.add(bullet)
            self.game.bullets.add(bullet)

class PlayerBullet(pg.sprite.Sprite): # Player's Bullet
    def __init__(self, x, y, angle):
        pg.sprite.Sprite.__init__(self)
        self.originalImage = pg.image.load(path.join(IMG_DIR, "laserRed16.png")).convert()
        self.originalImage.set_colorkey(BLACK)
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect()

        '''Properties in game'''
        self.travelAngle = radians(angle)
        self.rotate() # Bullet needs to spawn rotated so rotate in the init first
        self.bulletOffset = 50
        self.rect.centerx = x - self.bulletOffset * sin(self.travelAngle)
        self.rect.centery = y - self.bulletOffset * cos(self.travelAngle)
        self.speedx = -10 * sin(self.travelAngle)
        self.speedy = -10 * cos(self.travelAngle)
    
    def update(self):
        '''Update bullet coordinates and if it moves to the top of the screen, delete it'''
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

    def rotate(self):
        self.image = pg.transform.rotate(self.originalImage, degrees(self.travelAngle))
        self.rect = self.image.get_rect(center = self.rect.center)

class Enemy(pg.sprite.Sprite): # Parent sprite for all types of enemies
    def __init__(self, imageName, dimensions, name, game):
        pg.sprite.Sprite.__init__(self)
        self.dir = pg.image.load(path.join(IMG_DIR, imageName)).convert()
        self.image = pg.transform.scale(self.dir, dimensions)# Image directory
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() # Get the hitbox of the enemy
        self.radius = int(self.rect.width * 0.8 / 2)
        self.game = game

        '''Properties in game'''
        self.name = name
        self.rect.x = random.randrange(0, (SCREEN_WIDTH // 2) - self.rect.width + 1)
        self.rect.bottom = random.randrange(-50, -10)
        self.speedRanges = {"Normal": random.randrange(2, 5), "Fast": random.randrange(7, 10)} # So that I don't have to reference enemy's speed range
        self.resultantSpeed = "Normal"
        self.speedx = 0
        self.speedy = 0
        self.maxHP = 4
        self.currentHP = self.maxHP

        '''Minibar'''
        self.miniBar = StatsBar(PURPLE, BLACK, 20, 30, self.game.screen, 300, 20, self.currentHP, self.maxHP, "HP", self.rect.width // 2, 2, False)
        self.miniBar.draw("Minibar")

    def update(self):
        '''Update enemy state'''
        self.rect.x += self.speedx # Move the rect
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.right < -10 or self.rect.left > SCREEN_WIDTH // 2 + 10: # Move the sprite back to the top when it is not killed by player and it doesn't disappear off the screen
            self.rect.x = random.randrange(0, (SCREEN_WIDTH // 2) - self.rect.width + 1)
            self.rect.bottom = random.randrange(-80, -20)


# Types of enemies
class Bloon(Enemy):
    def __init__(self):
        super().__init__("Balloon.png", (100, 100), "Bloon", gameObject)
        '''Specific Properties to Bloon'''
        self.moveAngle = radians(random.randrange(-30, 31))
        self.speedx = self.speedRanges[self.resultantSpeed] * sin(self.moveAngle)
        self.speedy = self.speedRanges[self.resultantSpeed] * cos(self.moveAngle)

    def update(self):
        '''Update Bloon state'''
        super().update()
    
class StatsBar: # Class for all bars drawn
    def __init__(self, fillColour, bgColour, x, y, surface, barLength, barHeight, param1, param2, barType, textX, textY, drawText):
        self.fillColour = fillColour
        self.bgColour = bgColour
        self.xPos = x
        self.yPos = y
        self.surface = surface
        self.barLength = barLength
        self.barHeight = barHeight
        self.param1 = param1
        self.param2 = param2
        self.barType = barType
        self.drawText = drawText
        self.textX = textX
        self.textY = textY
        
    def draw(self, text):
        '''Draw and update the stats bar when necessary'''
        print(text)
        percentage = self.param1 / self.param2
        if percentage < 0:
            percentage = 0
        fill = percentage * self.barLength
        fillRect = pg.Rect(self.xPos, self.yPos, fill, self.barHeight)
        backgroundRect = pg.Rect(self.xPos, self.yPos, self.barLength, self.barHeight)
        outlineRect = pg.Rect(self.xPos - 5, self.yPos - 5, self.barLength + 10, self.barHeight + 10)
        pg.draw.rect(self.surface, self.bgColour, backgroundRect)
        pg.draw.rect(self.surface, self.fillColour, fillRect)
        pg.draw.rect(self.surface, WHITE, outlineRect, width = 5)
        if self.drawText == True:
            textToBeDrawn = str(self.param1) + "/" + str(self.param2) + " " + self.barType
            drawText(self.surface, textToBeDrawn, WHITE, 25, True, self.textX, self.textY)

class Game: # Main class that initialises everything required for the game, manages the main game loop and 
    def __init__ (self): 
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True

    def run(self): 
        '''Main runner loop that handles events'''
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000 # Obtain difference in time in seconds between frames
            self.getEvents()
            self.update()
            self.render()

    def update(self): 
        '''Updates based on events that have occured in the game'''
        self.allSprites.update()
        self.checkCollisions()

    def checkCollisions(self):
        '''Checks for sprite collisions''' # Better to do this in the main class because it is easier to manage and improves performance
        # Check if bullet hits a mob
        bulletHits = pg.sprite.groupcollide(self.bullets, self.enemies, True, False) # parameters: two sprite groups and if they should be killed
        for _, hitEnemies in bulletHits.items():
            for enemy in hitEnemies:
                if enemy.currentHP < self.player.damage:
                    self.player.cash += enemy.currentHP
                else:
                    self.player.cash += self.player.damage
                enemy.currentHP -= self.player.damage
                if enemy.currentHP <= 0:
                    enemy.currentHP = 0
                    enemy.kill()
                    self.enemies.remove(enemy)
                    self.spawnEnemies() # Spawn a mob when it is hit

        playerHits = pg.sprite.spritecollide(self.player, self.enemies, True, pg.sprite.collide_circle) # Better to use circle collisions so that the player is hit only when the enemy graphic touches the player
        for hit in playerHits:
            self.player.currentHP -= hit.currentHP
            if self.player.currentHP <= 0:
                self.player.currentHP = 0
                self.quitGame()
            self.spawnEnemies()

    def render(self): 
        '''Renders updated game states (sprites, objects etc.) into game and flip the board'''
        self.screen.fill(BLACK)
        self.backgroundDir = pg.image.load(path.join(IMG_DIR, "Background.jpeg")).convert() # Draw the game background
        self.backgroundImage = pg.transform.scale(self.backgroundDir, (601, 750))
        self.screen.blit(self.backgroundImage, (0, 0))
        self.allSprites.draw(self.screen) # Draw the sprites
        self.interfacebgRect = pg.Rect(SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT) # Parameters: top-left x, top-left y, bottom-right x, bottom-right y
        self.interfaceBackgroundSurface = self.screen.subsurface(self.interfacebgRect) # Subsurface is a child of surface
        self.interfaceBackgroundSurface.fill(DARK_GREY) # Draw the background of the user interface that displays healthbars, narrations, upgrades etc.
        self.drawInterface()
        pg.display.flip()

    def drawInterface(self):
        '''Method that draws everything needed to be put into the interface'''
        # Title
        self.drawTitle()
        # Player Stats Box
        self.drawPlayerStats()
        # Enhancement Modules Box
        self.drawUpgradeBox()
        # Enemy Stats Box
        self.drawEnemyStats()
     
    def drawTitle(self):
        '''Method that draws title interface'''
        drawText(self.interfaceBackgroundSurface, "Heads-Up-Display", WHITE, 40, True, 300, 30)
    
    def drawPlayerStats(self):
        '''Method that draws player interface'''
        self.playerStatsBox = pg.Rect(80, 90, 440, 240)
        self.playerStatsBoxSurface = self.interfaceBackgroundSurface.subsurface(self.playerStatsBox)
        self.playerStatsBoxSurface.fill(MODERATE_GREY)
        self.playerStatsBoxRect = pg.Rect(75, 85, 450, 245)
        pg.draw.rect(self.interfaceBackgroundSurface, WHITE, self.playerStatsBoxRect, width = 5)
        drawText(self.playerStatsBoxSurface, "Ship Status", LIGHT_BLUE, 30, True, 220, 18)
        self.playerHealthBar = StatsBar(GREEN, RED, 20, 60, self.playerStatsBoxSurface, 400, 20, self.player.currentHP, self.player.maxHP, "HP", 220, 62, True)
        self.playerHealthBar.draw("Healthbar")
        self.playerEXPBar = StatsBar(BLUE, BLACK, 20, 120, self.playerStatsBoxSurface, 400, 20, self.player.currentEXP, self.player.maxExp, "EXP", 220, 122, True)
        self.playerEXPBar.draw("EXPbar")
        drawText(self.playerStatsBoxSurface, "Cash", WHITE, 30, False, 20, 182.5)
        drawText(self.playerStatsBoxSurface, "Damage", WHITE, 30, False, 152.5, 182.5)
        drawText(self.playerStatsBoxSurface, "Lvl", WHITE, 30, False, 320, 182.5)
        self.playerCashBox = pg.Rect(85, 170, 50, 45)
        self.playerCashBoxSurface = self.playerStatsBoxSurface.subsurface(self.playerCashBox)
        self.playerCashBoxSurface.fill(BLACK)
        self.playerCashBoxRect = pg.Rect(80, 165, 60, 55)
        pg.draw.rect(self.playerStatsBoxSurface, WHITE, self.playerCashBoxRect, width = 5)
        cashString = str(self.player.cash)
        drawText(self.playerCashBoxSurface, cashString, LIGHT_GREEN, 30 if len(cashString) < 4 else 30 - len(cashString) - 1, True, 25, 12.5)
        self.playerDamageBox = pg.Rect(250, 170, 50, 45)
        self.playerDamageBoxSurface = self.playerStatsBoxSurface.subsurface(self.playerDamageBox)
        self.playerDamageBoxSurface.fill(BLACK)
        self.playerDamageBoxRect = pg.Rect(245, 165, 60, 55)
        pg.draw.rect(self.playerStatsBoxSurface, WHITE, self.playerDamageBoxRect, width = 5)
        damageString = str(self.player.damage)
        drawText(self.playerDamageBoxSurface, damageString, RED, 30 if len(damageString) < 4 else 30 - len(damageString) - 1, True, 25, 12.5)
        self.playerLevelBox = pg.Rect(365, 170, 50, 45)
        self.playerLevelBoxSurface = self.playerStatsBoxSurface.subsurface(self.playerLevelBox)
        self.playerLevelBoxSurface.fill(BLACK)
        self.playerLevelBoxRect = pg.Rect(360, 165, 60, 55)
        pg.draw.rect(self.playerStatsBoxSurface, WHITE, self.playerLevelBoxRect, width = 5)
        levelString = str(self.player.level)
        drawText(self.playerLevelBoxSurface, levelString, YELLOW, 30 if len(levelString) < 4 else 30 - len(levelString) - 1, True, 25, 12.5)

    def drawUpgradeBox(self):
        '''Method that draws the boxes for upgrades'''
        self.upgradeBox = pg.Rect(80, 365, 440, 150)
        self.upgradeBoxSurface = self.interfaceBackgroundSurface.subsurface(self.upgradeBox)
        self.upgradeBoxSurface.fill(LIGHT_GREY)
        self.upgradeBoxRect = pg.Rect(75, 360, 450, 155)
        pg.draw.rect(self.interfaceBackgroundSurface, WHITE, self.upgradeBoxRect, width = 5)
        drawText(self.upgradeBoxSurface, "Upgrade Enhancement Modules", YELLOW, 30, True, 220, 18)
        # TODO Upgrade Buttons

    def drawEnemyStats(self):
        '''Method that draws enemy interface'''
        self.enemyStatsBox = pg.Rect(80, 550, 440, 160)
        self.enemyStatsBoxSurface = self.interfaceBackgroundSurface.subsurface(self.enemyStatsBox)
        self.enemyStatsBoxSurface.fill(SUPER_DARK_GREY)
        self.enemyStatsBoxRect = pg.Rect(75, 545, 450, 165)
        pg.draw.rect(self.interfaceBackgroundSurface, WHITE, self.enemyStatsBoxRect, width = 5)
        drawText(self.enemyStatsBoxSurface, "Enemy Analytical Engine", RED, 30, True, 220, 18)
        # Check if the mouse has touched an enemy
        mouseLocation = pg.mouse.get_pos()
        for enemy in self.enemies:
            if enemy.rect.collidepoint(mouseLocation):
                drawText(self.enemyStatsBoxSurface, enemy.name, WHITE, 30, False, 20, 50)
                self.enemyHealthBar = StatsBar(PURPLE, BLACK, 20, 100, self.enemyStatsBoxSurface, 400, 20, enemy.currentHP, enemy.maxHP, "HP", 220, 102, True)
                self.enemyHealthBar.draw("Enemybar")

    def startNewGame(self): 
        '''Setup for new game'''
        self.totalWaves = 20
        self.currentWave = 1
        self.allSprites = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.player = Player(self)
        self.enemies = pg.sprite.Group()
        self.allSprites.add(self.player)
        for _ in range(15): # Limit the number of enemies in frame to 15
            self.spawnEnemies()
        self.run()

    def showStartScreen(self): 
        '''Display start screen'''
        pass

    def showGameOverScreen(self): 
        '''Display game over screen'''
        pass

    def quitGame(self): 
        '''Procedures when game is quit'''
        if self.playing == True:
            self.playing = False
        self.running = False

    def getEvents(self): 
        '''Manages all events that happen within the game loop'''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quitGame()

    def spawnEnemies(self):
        '''Method that manage mob spawning; for now, there is only 1 type of mob'''
        bloon = Bloon()
        self.allSprites.add(bloon)
        self.enemies.add(bloon)

# Global procedures which lie outside the game class - programming to an interface
        
def drawText(surface, text, color, size, midtop, x, y):
    font = pg.font.Font(FONT_NAME, size)
    textSurface = font.render(text, True, color)
    textRect = textSurface.get_rect()
    if midtop == True:
        textRect.midtop = (x, y)
    else:
        textRect.topleft = (x, y)
    surface.blit(textSurface, textRect)

def round2(number):
    roundedNumber = round(number)
    if roundedNumber % 2 != 0:
        roundedNumber += 1
    return number

# Run game -- instantiation is needed
if __name__ == "__main__":
    gameObject = Game()
    while gameObject.running:
        gameObject.showStartScreen()
        gameObject.startNewGame()
        gameObject.showGameOverScreen()

pg.quit()