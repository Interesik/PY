import random
import Helper


# abstrakcja Zwierzęcia
class Animal:
    # move
    def move(self):
        raise NotImplementedError("Metoda abstrakcyjna")

    def respawn(self, init_pos_limit):
        raise NotImplementedError("Metoda abstarakcyjna")

    def __str__(self):
        return "Animal:"

    def check_postion(self, init_pos_limit):
        if init_pos_limit > 0:
            Helper.logging.debug(str(self) + ", is check if don't cross limit")
            if self.pos[1] > init_pos_limit:
                Helper.logging.debug(
                    str(self) + ", crossed a limit, by: " + str(self.pos[1]
                                                                - init_pos_limit))
                self.pos[1] = init_pos_limit
            if self.pos[0] > init_pos_limit:
                Helper.logging.debug(
                    str(self) + ", crossed a limit, by: " + str(self.pos[0]
                                                                - init_pos_limit))
                self.pos[0] = init_pos_limit


# Wilk dziedziczy z Animal
class Wolf(Animal):

    def __init__(self, wolf_move_dist):
        self.wolf_move_dist = wolf_move_dist
        self.id = 0
        self.respawn(0)

    def move(self, init_pos_limit, sheep, dist):
        # szukam wektora jednostkowego dla (Sheep,wolf)
        Helper.logging.debug(str(self) + " moving to " + str(sheep))
        x = sheep.pos[0] - self.pos[0]
        y = sheep.pos[1] - self.pos[1]
        self.pos[1] += self.wolf_move_dist * y / dist
        self.pos[0] += self.wolf_move_dist * x / dist
        self.pos[0] = round(self.pos[0], 3)
        self.pos[1] = round(self.pos[1], 3)

    def __str__(self):
        return "Wolf, ID = " + str(self.id) + ", Pos = " + str(self.pos)

    def eat(self, sheep):
        Helper.logging.debug(str(self) + ", eat and move to " + str(sheep))
        self.pos = sheep.pos
        sheep.eaten()

    def respawn(self, init_pos_limit):
        self.pos = [0, 0]
        Helper.logging.debug(str(self) + ", have been spawn")


# Owca dziedziczy z Animal
class Sheep(Animal):
    random.seed()
    directions = ([1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0])
    id = int(1)

    def eaten(self):
        print("Has been eaten:", self)
        Helper.logging.debug(str(self) + ", is set to [None],[None]")
        self.pos = [None, None]

    def respawn(self, init_pos_limit):
        if init_pos_limit > 0:
            self.pos = [
                round(random.triangular(-init_pos_limit, init_pos_limit), 3),
                round(random.triangular(-init_pos_limit, init_pos_limit), 3)]
        else:
            self.pos = [round(random.triangular(-100, 100), 3),
                        round(random.triangular(-100, 100), 3)]
        Helper.logging.debug(str(self) + ", was set on Meadown")

    # Inicjalizator
    def __init__(self, sheep_move_dist, init_pos_limit):
        self.pos = []
        self.respawn(init_pos_limit)
        self.sheep_move_dist = sheep_move_dist
        self.id = Sheep.id
        Sheep.id += 1

    def move(self, init_pos_limit):
        if self.pos == [None, None]:
            Helper.logging.debug(str(self) + ", is not moving")
            return
        Helper.logging.debug(str(self) + ", is moving")
        chosen_path = random.choice(self.directions)
        self.pos[0] += chosen_path[0] * self.sheep_move_dist
        self.pos[1] += chosen_path[1] * self.sheep_move_dist
        self.pos[0] = round(self.pos[0], 3)
        self.pos[1] = round(self.pos[1], 3)
        self.check_postion(init_pos_limit)
        Helper.logging.debug(str(self) + ", was moved")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return " Sheep, ID = " + str(self.id) + ", Pos = " + str(self.pos)

    def __repr__(self):
        return str(self.pos)
