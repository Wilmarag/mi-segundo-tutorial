import pygame
import sys
import random
import math
import os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
#---------TENER TODO DIVIDIDO EN UNA CLASE PRINCIPAL---------------------------------------------------------------------------------

class Game:
    #----contruct
    def __init__(self):
        pygame.init()
        #-------NOMBRE DEL JUEGO--------------------------------------------------------------------------
        pygame.display.set_caption('Ninja Game')
        #-------------------------------------------------------------------------------------------------
        self.screen = pygame.display.set_mode((640,480))
#modificar el tamaño de la imagen para que se puede visualizar con respecto al tamaño de la pantalla
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
    #-------------------------- no renderizar todas las cosas en la misma pantalla, ponemos las cosas menos importantes en segundo plano
        self.display_2 = pygame.Surface((320, 240))
    #---------------------------------------------------------------------------------------------------------------------
        self.clock = pygame.time.Clock()
        #//self.img = pygame.image.load('Imagenes/clouds/cloud_1.png')
        #//self.img.set_colorkey((0, 0, 0))
        #//self.img_pos = [160, 260]
        self.movement = [False, False]

        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'spawners' : load_images('tiles/spawners'),
            'stone' : load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds' : load_images('clouds'),
            #--------------------animacion de los enemigos------------------------------------------------
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=4),
            #---------------------------------------------------------------------------------------------
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun' : load_image('gun.png'),
            'projectile' : load_image('projectile.png'),
        }
#----------------------musica y efectos del juego---------------------------------------------------------------------------
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['shoot'].set_volume(0.4)
#---------------------------------------------------------------------------------------------------------------------------
        #//self.collision_area = pygame.Rect(50, 50, 300, 50)
#---------------traemos las nubes--------------------------------------------
        self.clouds = Clouds(self.assets['clouds'], count=16)
#------------------------------------------------------------------------------
#traemos al jugardor al codigo principal
        self.player = Player(self,(50, 50), (8, 15))
#-------------------------------------------------------------------------------------------------------------------------------------
#---------------------------traemos los mosaicos o mapa a la ventana------------------------------------------------------------------
        self.tilemap = Tilemap(self, tile_size=16)
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------cargar los nivel de los mapas----------------------------------
        self.level = 0
#----------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------cargar el mapa editado con las animaciones del jugador----------------------------------------------------
        self.load_level(self.level)
#-------------------------------------------------------------------------------------------------------------------------------------
#--------------------
        self.screenshake = 0
#----------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------cargar los mapas y a limpiar todos los residuos de pixeles de memoria, y simplemente reiniciar todo-----------
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

    #----------------------------
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 +  tree['pos'][1], 23, 13))
    #-------------------------------------------------------------------------------------------------------------------------------------
    #-----------------------------spawner para la cracion de los enemigos-----------------------------------------------------------------
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------
        self.particles = []
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------proyectiles de los NPC disparados de las armas----------------------------------------
        self.projectiles = []
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------
        self.sparks = []
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------traemos el desplazamiento del mundo------------------------------------------------------------------------
        self.scroll = [0, 0]        
    #-------------------------------------------------------------------------------------------------------------------------------------
    #----------------------eliminacion del jugador-----------------------------------
        self.dead = 0
    #-----------------------------------------------------------------------------------------------------------------
    #----------------------transición entre lvl
        self.transition = -30

    #------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
    def run(self):
    #-----------------musica del juego, por un numero de bucles que se desee---------------------------------------
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)
    #----------------------------------------------------------------------------------------------------------------------------------
        while  True:
            self.display.fill((0, 0, 0, 0))
#RENDERIZAR LOS FOTOGRAMAS DE LA VENTA PARA QUE NO DEJEN RASTRO 
            self.display_2.blit(self.assets['background'], (0, 0))
#-------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------
            self.screenshake = max(0, self.screenshake - 1)
    #----------------------------------------------------------------------------------------------------------------------------------
        #------------------cambio de lvl-------------------------------------------
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level += min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1
        #------------------------------------------------------------------------------------------------------------------------------
        #--------------------------------------muerte del jugador 
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)
                
        #----------------------------------------------------------------------------------------------------------------------------------------
#-----------movimiento del mapa con respecto al movimiento del jugador------------------------------------------------------------------------------------------------------
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

#-------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y +random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
#--------------------------------------------------------------------------------------------------------------------------------------
#---------------------cargamos al mapa las nuves con su respectivo movimiento----------------------------------------------
            self.clouds.update()
            self.clouds.render(self.display_2, offset= render_scroll)
#--------------------------------------------------------------------------------------------------------------------------
#---------------------CARGAMOS EL MAPA RENDERIZADO-----------------
            self.tilemap.render(self.display, offset = render_scroll)

            #//img_r = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())
            #//if img_r.colliderect(self.collision_area):
                #//pygame.draw.rect(self.screen, (0, 100, 255), self.collision_area)
            #//else:
                #//pygame.draw.rect(self.screen, (0, 50, 155), self.collision_area)

#CALCULAR LA POSICION CON CADA MOVIMIENTO utilizando procedimiento de globos
            #//self.img_pos[1] += self.movement[1] - self.movement[0] * 5
#BLIT SE USA PARA UTILIZAR LA IMAGEN COMO UN MOSAICO 
            #//self.screen.blit(self.img, self.img_pos )
        #-------------------corremos la intrucción para el movimiento y pusta de los enemigos------------------------------------------------
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
    #------------------------------------------------------------------------------------------------------------------------------------
        #--------------------------------
            if not self.dead:
        #-------------------------------------------------------------------------------------------------------------------------------------------
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)
    #----------------------([[x, y], direction, timer])vamos a proteger al jugador cuando de la velocidad, sobre los proyectiles-----------------------------
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                #---------------- para que el proyectil no continue por todo el mapa volando
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        #---------------------impacto al jugador---------------------
                        self.dead += 1
                        #--------------------------------------------------------------------------------
                        #------------------------sonido 
                        self.sfx['hit'].play()
                        #-------------------------------------------------------------------------------------------------------------------
                        self.screenshake = max(16, self.screenshake)
                        #----------se escriben los argumentos para sean de igual manera y al azar---------------------------------
                        for i in range(30):
                            angle = random.random() * math.pi * 2 
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                        #---------------------------------------------------------------------------------------------------------
                #---------------------------------------------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
                
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #----------------------enmascaramos el display principal; variacion de colores
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---------------------------------------------------
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset =render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) *0.3
                if kill:
                    self.particles.remove(particle)
    #---------------------------------------------------------------------------------------------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
#---------------FUNCION DE MOVIMINETO EN EL TECLADO-----------------------------------------------------------------------------------------------------
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    #-------------------------------
                    if event.key == pygame.K_x:
                        self.player.dash() 
                    #--------------------------------------------------------------------------------------
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
#----------------------------------------------------------------------------------------------------------------------------------------
#--------------------------ventana de cambio de nivel-------------
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
#----------------------------------------------------------------------------------------------------------------------------------------
            self.display_2.blit(self.display, (0, 0))
#--------------------------
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
#----------------------------------------------------------------------------------------------------------------------------------------
#transformamos el tamaño de la venta y los objetos todos juntos
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
#----------------------------------------------------------------------------------------------------------------------------------------
            pygame.display.update()
            self.clock.tick(60)

#---------CORRER EL OBJ------------------------------------------------------------------------------------------------------------------
Game().run()