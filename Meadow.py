import random
import json
import csv
import argparse
from pathlib import Path

#TODO: configparser -c/--config, logging package -l/--log, create package
parser = argparse.ArgumentParser(description="Wolf catch Sheeps game.")
parser.add_argument('-r', '--rounds', type=int, metavar='', help='Define number of rounds,'
                                                                 ' if not defined game simulated to last sheep.')
parser.add_argument('-s', '--sheep', type=int, metavar='',
                    help='Define number of sheeps, if not defined 10 are created.')
parser.add_argument('-w', '--wait', action='store_true', help="Pause after each round.")
parser.add_argument('-d', '--dir', type=Path, metavar='', help='Path to save diagnostic files,'
                                                              ' if not defined current directory.')


args = parser.parse_args()


# Plansza
class Meadown:
    round_ = 1
    list_alive = []
    jsondump = ""
    max_round = None
    wolf = None
    sheep_dist_dict = {}
    num_sheeps = None
    init_pos_limit = None

    def __init__(self, sheep_speed, wolf_speed, max_round, num_sheeps, init_pos_limit=0):
        self.init_pos_limit = init_pos_limit
        if num_sheeps is not None:
            self.num_sheeps = num_sheeps
        else:
            self.num_sheeps = 15
        self.wolf = Wolf(wolf_speed)
        if max_round is not None:
            self.max_round = max_round
        else:
            self.max_round = 50
        self.jsondump = '{"Rounds":[\n'
        for _ in range(self.num_sheeps):
            self.sheep_dist_dict.update({Sheep(sheep_speed, init_pos_limit): 0})

    def count_disc(self, sheep, wolf):
        if sheep.pos[0] is None:
            return None
        else:
            return round(((sheep.pos[0] - wolf.pos[0]) ** 2 + (sheep.pos[1] - wolf.pos[1]) ** 2) ** 0.5, 3)

    def sheeps_turn(self):
        for s in self.sheep_dist_dict.keys():
            s.move(self.init_pos_limit)
            self.sheep_dist_dict[s] = self.count_disc(s, self.wolf)

    def wolf_turn(self):
        closest_sheep = min(self.sheep_dist_dict, key=lambda k: self.sheep_dist_dict[k] if
        self.sheep_dist_dict[k] is not None else float('inf'))

        if self.sheep_dist_dict.get(closest_sheep) < self.wolf.wolf_move_dist:
            self.wolf.eat(closest_sheep)
            # self.sheep_dist_dict.pop(closest_sheep)
            self.num_sheeps -= 1
        else:
            print("Try to catch:", closest_sheep)
            self.wolf.move(self.init_pos_limit, closest_sheep, self.count_disc(closest_sheep, self.wolf))

    def round(self):
        self.sheeps_turn()
        print(self)
        self.jsondump += json.dumps(self, default=self.endcode_Meadown, indent=3)
        self.jsondump += ',\n'
        self.list_alive.append([self.round_, self.num_sheeps])
        self.wolf_turn()
        if args.wait:
            input("Press Enter to continue...")
        self.round_ += 1

    def play(self):
        while self.num_sheeps and self.round_ != self.max_round:
            self.round()
        print("end of game.")
        self.jsondump = self.jsondump[:-2]
        self.jsondump += '\n]}'
        if args.dir is not None:
            args.dir.mkdir(parents=True, exist_ok=True)
            with open(str(args.dir)+'/pos.json', 'w', encoding='utf-8') as pos_log:
                pos_log.write(self.jsondump)

            with open(str(args.dir)+'/alive.csv', 'w', encoding='utf-8', newline='') as alive_csv:
                writer = csv.writer(alive_csv)
                writer.writerows(self.list_alive)
        else:
            with open('pos.json', 'w', encoding='utf-8') as pos_log:
                pos_log.write(self.jsondump)

            with open('alive.csv', 'w', encoding='utf-8', newline='') as alive_csv:
                writer = csv.writer(alive_csv)
                writer.writerows(self.list_alive)
    def __str__(self):
        return "Meadown: Round: " + str(self.round_) + " size: " + str(
            self.init_pos_limit) + "\nnumber_of_sheeps: " + str(
            self.num_sheeps) + "\n" + str(self.wolf) + "\nSheeps: " + str(list(self.sheep_dist_dict.keys()))

    def endcode_Meadown(self, o):
        if isinstance(o, Meadown):
            return {'round_no': str(self.round_), 'wolf_pos': str(self.wolf.pos),
                    'sheep_pos': str(list(self.sheep_dist_dict.keys()))}
        else:
            raise TypeError()


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
            if self.pos[1] > init_pos_limit:
                self.pos[1] = init_pos_limit
            if self.pos[0] > init_pos_limit:
                self.pos[0] = init_pos_limit


# Wilk dziedziczy z Animal
class Wolf(Animal):

    def __init__(self, wolf_move_dist):
        self.pos = [0, 0]
        self.wolf_move_dist = wolf_move_dist
        self.id = 0

    def move(self, init_pos_limit, sheep, dist):
        # szukam wektora jednostkowego dla (Sheep,wolf)
        x = sheep.pos[0] - self.pos[0]
        y = sheep.pos[1] - self.pos[1]
        self.pos[1] += self.wolf_move_dist * y / dist
        self.pos[0] += self.wolf_move_dist * x / dist
        self.pos[0] = round(self.pos[0], 3)
        self.pos[1] = round(self.pos[1], 3)

    def __str__(self):
        return "Wolf, ID = " + str(self.id) + ", Pos = " + str(self.pos)

    def eat(self, sheep):
        self.pos = sheep.pos
        sheep.eaten()

    def respawn(self, init_pos_limit):
        self.pos = [0, 0]


# Owca dziedziczy z Animal
class Sheep(Animal):
    random.seed()
    directions = ([1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0])
    id = int(1)

    def eaten(self):
        print("Has been eaten:", self)
        self.pos = [None, None]

    def respawn(self, init_pos_limit):
        if init_pos_limit > 0:
            self.pos = [round(random.triangular(-init_pos_limit, init_pos_limit), 3),
                        round(random.triangular(-init_pos_limit, init_pos_limit), 3)]
        else:
            self.pos = [round(random.triangular(-100, 100), 3),
                        round(random.triangular(-100, 100), 3)]

    # Inicjalizator
    def __init__(self, sheep_move_dist, init_pos_limit):
        self.pos = []
        self.respawn(init_pos_limit)
        self.sheep_move_dist = sheep_move_dist
        self.id = Sheep.id
        Sheep.id += 1

    def move(self, init_pos_limit):
        if self.pos == [None, None]:
            return
        chosen_path = random.choice(self.directions)
        self.pos[0] += chosen_path[0] * self.sheep_move_dist
        self.pos[1] += chosen_path[1] * self.sheep_move_dist
        self.pos[0] = round(self.pos[0], 3)
        self.pos[1] = round(self.pos[1], 3)
        self.check_postion(init_pos_limit)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return " Sheep, ID = " + str(self.id) + ", Pos = " + str(self.pos)

    def __repr__(self):
        return str(self.pos)


if __name__ == "__main__":
    m = Meadown(0.5, 1, args.rounds, args.sheep)
    m.play()
