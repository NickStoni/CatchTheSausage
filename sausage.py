import config
class Sausage:
    def __init__(self,x,y,edible,img):
        self.x_1 = x
        self.x_2 = x+config.FOOD_SIZE
        self.y_1 = y
        self.y_2 = y+config.FOOD_SIZE
        self.edible = edible
        self.image = img