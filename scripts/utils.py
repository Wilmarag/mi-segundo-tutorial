import pygame
import os #listador que permite realizar operaciones relacionadas con la gestion de archivos 

BASE_IMG_PATH = 'data/Imagenes/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img
#------------------------------------crear una funcion para cargar todos los mosaicos --------------------------------------------------------------------
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
    #aqui cargamos las imagenes listandolas
        images.append(load_image(path + '/' + img_name))
    return images
#----------------------------------------------------------------------------------------------------------------------
#-----------------------------------crear las animaciones representandolas como un objeto----------------------------------------------------------------
class Animation:
    #animaremos las imagenes por fotogramas y la duracion de cada fotograma------------------------------------------------------------------------------
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        #----------------------validaremos si se esta realizando el bucle de la animacion y estamos validando donde nos encontramos-----------------------
        self.done = False
        self.frame = 0
        #-------------------------------------------------------------------------------------------------------------------------------------------------
    #------------------------------------------------copiamos las animaciones para modifica la copia
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    #------------------------------------------------------------------------------------------------
    def update(self):
        #bucle para asegurarse que la lista de imagnes se recorrar sin error y no llegue a su final de animacion. duracion de la imagen por len para forzar el enmarcado en el bucle------------------------------------------
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
        #------------------------------------------------------------------------------------------------------------------------------------------------- 
    #----------------------------renderizamos las animaciones, incrementamos el valor por nuestro cuadro y el marco del juego----------------------------
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    #------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------