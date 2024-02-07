import random

#---------------dibujo, posición de las nubes y movimiento por la pantalla de pixeles por tiempo predeterminado-------------------------------------------------------
class Cloud:
    def __init__(self, pos, img, speed,depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed
    
    def render(self, surf, offset=(0, 0)):
        #si se mueve la profundidad 0.5 y la camara 5 pixeles a la derecha la nube se mueva 2.5 pixeles
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        #------------------------------------------------------------------------------------------------
        #crea un limite determinado de nubes y las mueve por toda la venta, dejamos espacio para anexar mas bucles
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))
        
        #clasificación que determina como se usan los objetos normalmete en este caso son las nubes por profundidad
        self.clouds.sort(key= lambda x: x.depth)
        #-----------------------------------------------------------------------------------------------

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset = (0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)