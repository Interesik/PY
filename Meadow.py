import Animal
import Helper
import json
import csv


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
        self.wolf = Animal.Wolf(wolf_speed)
        if max_round is not None:
            self.max_round = max_round
        else:
            self.max_round = 50
        self.jsondump = '{"Rounds":[\n'
        for _ in range(self.num_sheeps):
            self.sheep_dist_dict.update({Animal.Sheep(sheep_speed, init_pos_limit): 0})

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
        if Helper.args.wait:
            input("Press Enter to continue...")
        self.round_ += 1

    def play(self):
        Helper.logging.info('Started simulation')
        while self.num_sheeps and self.round_ != self.max_round:
            Helper.logging.info("round "+str(self.round_))
            self.round()
        Helper.logging.info("end of game.")
        print("end of game.")
        self.jsondump = self.jsondump[:-2]
        self.jsondump += '\n]}'
        if Helper.args.dir is not None:
            Helper.logging.info("Saving json and csv to file: " + str(Helper.args.dir) + '/pos.json' + str(Helper.args.dir) + '/alive.csv')
            with open(str(Helper.args.dir) + '/pos.json', 'w', encoding='utf-8') as pos_log:
                pos_log.write(self.jsondump)

            with open(str(Helper.args.dir) + '/alive.csv', 'w', encoding='utf-8', newline='') as alive_csv:
                writer = csv.writer(alive_csv)
                writer.writerows(self.list_alive)
        else:
            Helper.logging.info("Saving json and to file: "+'pos.json and alive.csv')
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


if __name__ == "__main__":
    m = Meadown(Helper.c_parser.getfloat('Movement', 'SheepMoveDist', fallback=0.5),
                Helper.c_parser.getfloat('Movement', 'WolfMoveDist', fallback=1), Helper.args.rounds, Helper.args.sheep)
    m.play()
