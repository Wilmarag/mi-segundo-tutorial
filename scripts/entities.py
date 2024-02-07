import pygame
import math, random

from scripts.particle import Particle
from scripts.spark import Spark

#REALIZAR EL SEGUIMIENTO DE LOS PROCESOS Y TENER LAS COSAS ORGANIZADAS; RECONOCER LAS ENTIDADES, TIPOS, TAMAÑOS
class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
#---------------------------------------------------------------------------------------------------------------------------------------------------------
#LISTAMOS TODO EN LA FUNCION LSIT PARA CONVERTIR CUALQUIER ITERABLE; ASEGURARSE QUE CADA ENTIDAD TENGA UNA LISTA PARA SU ACTUALIZACIONES MUTUAS
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions ={'up': False, 'down': False, 'right': False, 'left': False}
#---------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------animaciones, conectada por la cadena---------------------------------------------------------------------
        self.action = ''
        self.anim_offset =(-3, -3)
        self.flip = False
        self.set_action('idle')
#---------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------variable del ultimo moviemiento en el salto ----------------------------------
        self.last_movement = [0, 0]
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#DETENCION DE LAS COLISIONES POR MEDIO DE LOS RECTANGULOS Y DE MANERA DINAMICA PARA NO ESTAR ACTULIZANDO TODO EL TIEMPO 
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
#---------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------se especifica cuanda cada futograma de la animacion ha cambiado, y verificar si cada cambio corresponde a la animación-------------------------------------------------------------------------------------------------------------------------
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
#-------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def update(self, tilemap, movement=(0, 0)):
        self.collisions ={'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
#------------------detectamos las coliciones con los azulejos primero en el eje X----------------------------------------------------------------------------------------------
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------detectamos las colisiones de los asulejen en el sentido contrario-----------------------------------------------------------------------
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
#------------------detectamos las coliciones con los azulejos primero en el eje X----------------------------------------------------------------------------------------------
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------- vista del player con el movimineto he identifique si esta mirando a la derecha o izquierda-------------------------------------------------------------------------------------------
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
#---------------------------------------------------------------------------------------------------------------------
#-------------------------------
        self.last_movement = movement
#-------------------------------------------------------------------------------------------------------------------------
#incorporamos la gravedad al jugador en relacion a los mosaicos.
        self.velocity[1] = min(5, self.velocity[1] + 0.1 )
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#despues de generar el movimiento correcto pasamos a renderizar
    def render(self, surf, offset = (0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        #surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))
#----------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------movimientos para los enemigos, animacions-------------------------------------------------------------------
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
        #--------------(pixeles)le damos al movimiento el valor de cero ya que es la clave del movimiento, dando valores negativos dependiendo del flip
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        #-----------------------------sonido del disparo---------------------------------------------------------------------------
                        self.game.sfx['shoot'].play()
                        #--------------------------------------------------------------------------------------------------------------------------
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery]], -1.5, 0)
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))

                    if (not self.flip and dis[0] > 0):
                        #-----------------sonido del disparo----------------------------------------------
                        self.game.sfx['shoot'].play()
                        #--------------------------------------------------------------------------------------------------------------------------
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        #-----------------------------------------------------------------------------
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        super().update(tilemap, movement=movement)
        #-----------------------funciones de los enemigos, movimientos por pixel*segundo
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        #---------------------------------------------------------------------------------------------------------------------------------------- 
        #-------------------------
        if abs (self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
        #----------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------escondemos al jugador detras de un objeto y volvemos a llamar la funcion principal
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        #--------------------------------
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
        #----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------    
#------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------movimiento para el jugador, tiempo en el aire y corriendo---------------------------------------------------
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
    #---------------------
        self.jumps = 1
        self.wall_slide = False
    #-----------------------------------------------------------------------------------------
    #-------------------------------
        self.dashing = 0
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        #---------------cuando se cae el jugador
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead = 1
        #---------------------------------------------------------------------------------------------------------------
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
        #---------------
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            #----------------------------
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            #--------------------------------------------------------------------------------------------------------
            self.set_action('wall_slide')
        #----------------------------------------------------------------------------------------------------
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        #------------------------
        #-----------------------generando una velocidad basada en el ángulo y así es como mueves algo en una dirección.
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angel = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angel) * speed, math.sin(angel) * speed]            
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        #---------------------------------------------------------------------------------------------------------------------
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            #-----------------------Lo que estamos haciendo aquí es eso al final de estos primeros 10 fotogramas de nuestro guión. Vamos a reducir drásticamente nuestra velocidad y provocar una para repentina en el dash
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
            #---------------------------------------------------------------------------------------------------------------------
        #-------------------------------------------------------------------------------------------------------------------------
        #------------------------
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)   
        #---------------------------------------------------------------------------------------------------------------------
    #--------------------------------para generarle un cooldowm en el dash
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
    #------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------control sobre el movimiento del saltado para que no quede infinito----------------------------
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
    #------------------------------------------------------------------------------------------------------------------------------      
    #---------------------
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
    #---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------