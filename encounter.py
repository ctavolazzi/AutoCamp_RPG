
from enemy import Enemy
from player import Player
from inanimate import Inanimate
from random import randint
from math import floor


class Encounter:
    def __init__(self, max_inventory):
        self.currentEntity = None
        self.animateList = list()
        self.inanimateList = list()
        self.mapList = list()
        self.gamerule_inv_max = max_inventory   # Gamerule that determines if there will be max inventory size.
        self.turnCounter = 0
        self.live = False
        self.map_max_x = 0
        self.map_max_y = 0

    def get_entity(self, is_animate, index):
        if is_animate:
            return self.animateList[index]
        else:
            return self.inanimateList[index]

    def get_actor(self):
        return self.currentEntity

    def get_al_size(self):
        return len(self.animateList)

    def add_entity(self, ent):
        if isinstance(ent, Inanimate):
            self.inanimateList.append(ent)
        else:
            self.animateList.append(ent)
            if self.live:
                self.turnCounter = self.turnCounter % (len(self.animateList) - 1)
                self.determineInitiative()

    def start_encounter(self):
        self.determineInitiative()
        self.currentEntity = self.animateList[0]
        self.live = True

    def enemyInRange(self):
        location = self.currentEntity.get_coors()
        x, y, z = location[0], location[1], location[2]
        nearbyCoors = []
        inRange = []

        if y > 1:  # N
            nearbyCoors.append([x, y - 1, z])
        if y > 1 and x < self.map_max_x:  # NE
            nearbyCoors.append([x + 1, y - 1, z])
        if x < self.map_max_x:  # E
            nearbyCoors.append([x + 1, y, z])
        if y < self.map_max_y and x < self.map_max_x:  # SE
            nearbyCoors.append([x + 1, y + 1, z])
        if y < self.map_max_y:  # S
            nearbyCoors.append([x, y + 1, z])
        if y < self.map_max_y and x > 1:  # SW
            nearbyCoors.append([x - 1, y + 1, z])
        if x > 1:  # W
            nearbyCoors.append([x - 1, y, z])
        if x > 1 and y > 1:  # NW
            nearbyCoors.append([x - 1, y - 1, z])

        for ent in self.animateList:
            if ent.get_iff():
                otherCoors = ent.get_coors()
                if otherCoors in nearbyCoors:
                    inRange.append(ent)

        return inRange

    # ===============================================================================
    # Map & Movement Methods
    # ===============================================================================
    # def map_display(self):
    #     for i in range(0, len(self.entityList)):
    #         print(self.animateList[i].get_name() + " is taking up " + self.animateList[i].get_size() + " of tile (" +
    #               self.animateList[i].get_coors()[0] + ", " + self.animateList[i].get_coors()[1] + ")")

    def enc_move(self, actor, new_x_coord, new_y_coord, new_z_coord=1):
        x_coord = actor.get_coors()[0]
        y_coord = actor.get_coors()[1]
        testing = [new_x_coord, new_y_coord, new_z_coord]

        if new_x_coord > self.map_max_x or new_y_coord > self.map_max_y:
            return "[ER] Out of bounds!"

        for ent in self.animateList:
            if ent.get_coors() == testing and ent != actor:
                return "[ER] That space is occupied!"

        requested_distance = 0
        if actor.get_coors()[0] == new_x_coord:
            requested_distance = abs(actor.get_coors()[0] - new_x_coord) * 5
        elif actor.get_coors()[1] == new_y_coord:
            requested_distance = abs(actor.get_coors()[1] - new_y_coord) * 5
        else:
            requested_distance = (abs(actor.get_coors()[0] - new_x_coord) * 5) + (
                    abs(actor.get_coors()[1] - new_y_coord) * 5)
        if requested_distance > actor.get_stat("Speed"):
            return "[ER] You're not fast enough! (Speed {})".format(actor.get_stat("Speed"))

        self.mapList[y_coord - 1][(x_coord + ((1 * x_coord) - 1))] = ' '
        actor.set_coors(new_x_coord, new_y_coord, new_z_coord)
        return False

    def enc_fill_map(self, width, height):
        self.map_max_x = width
        self.map_max_y = height
        for i in range(0, height):
            newRow = list()
            newRow.append('|')
            for i in range(0, width):
                newRow.append(' ')
                newRow.append('|')
            self.mapList.append(newRow)

    def enc_update_map(self):
        for i in range(0, len(self.animateList)):
            xCoord = self.animateList[i].get_coors()[0]
            yCoord = self.animateList[i].get_coors()[1]
            self.mapList[yCoord - 1][(xCoord + ((1 * xCoord) - 1))] = self.animateList[i].get_name()[0]

    def enc_print_map(self):
        print()
        for i in range(0, len(self.mapList)):
            for j in range(0, len(self.mapList[i])):
                print(self.mapList[i][j], end='')
            print("")

    # ===============================================================================
    # Inventory Methods
    # ===============================================================================
    def inv_pickup(self, item, amount, hot_swap, is_armor, notify=True):
        if hot_swap:
            self.currentEntity.inv_add(item, amount)
            self.inv_equip(is_armor, item, notify)
        else:
            self.currentEntity.inv_add(item, amount)

    def inv_discard(self, item_name, amount):
        self.currentEntity.inv_remove(item_name, amount, True, False)

    def inv_sell(self, item_name, amount):
        self.currentEntity.inv_remove(item_name, amount, False, True)

    def inv_use(self, item_name, notify=True):
        item = self.currentEntity.find_item(item_name, False)
        if item and not item.get_is_weapon() and not item.get_is_armor():
            if self.currentEntity.inv_remove(item, 1, False, False, False):
                if notify:
                    print("[OK] You used ", item.get_name(), "!")
                return True
        elif item:
            print("[ER] Item is not consumable!")
        else:
            print("[ER] You don't have that item!")

        return False

    def inv_give(self, acceptor, item_name, amount):
        if not acceptor.is_enemy() and not acceptor.inv_is_full(False):
            item = self.currentEntity.inv_remove(item_name, amount, False, False)
            acceptor.inv_add(item)
            print("[OK] You gave", acceptor.get_name(), " ", item_name, "!")
        elif acceptor.inv_is_full(False):
            print("[ER] ", acceptor.get_name(), "'s inventory is full!")

    def inv_equip(self, is_armor, item, notify=True):
        item = self.currentEntity.inv_remove(item, 1, False, False, notify)
        if is_armor:
            armor = self.currentEntity.get_armor()
            if armor is not None:
                self.currentEntity.inv_add(armor, 1)
            self.currentEntity.set_armor(item)
            if notify:
                print("[OK]: You have swapped your armor!")
        else:
            weapon = self.currentEntity.get_weapon()
            if weapon is not None:
                self.currentEntity.inv_add(weapon, 1)
            self.currentEntity.set_weapon(item)
            if notify:
                print("[OK]: You have swapped your weapon!")

    # ===============================================================================
    # Dice & Check Methods
    # ===============================================================================
    @staticmethod
    def rollDice(rolls, numOfFaces, print_results=True) -> int:
        total = 0

        validFaces = [4, 6, 8, 10, 12, 20]
        if numOfFaces not in validFaces:
            print(str(numOfFaces) + " is not a valid number of faces!!")
            print("Valid dice are: d4, d6, d8, d10, d12, and d20.")
            return total

        if (rolls < 1) or (type(rolls) != int):
            print("Rolls must be whole numbers > 1!!")
            return total

        for roll in range(rolls):
            result = randint(1, numOfFaces)
            total += result

            if print_results:
                print("Rolling D{} {} of {}... Result is {}".format(numOfFaces, roll + 1, rolls, result))
        if print_results:
            print("Final total is... {}!!".format(total))
        return total

    def modifier(self, stat, ent):
        return floor(((ent.get_stat(stat)) - 10) / 2)

    def performCheck(self, stat, ent, advantage=False, disadvantage=False, print_results=True):
        roll = 0
        roll1 = self.rollDice(1, 20, False)
        roll2 = self.rollDice(1, 20, False)
        if (advantage and disadvantage) or (not advantage and not disadvantage):
            roll = roll1
        elif advantage:
            roll = max(roll1, roll2)
        elif disadvantage:
            roll = min(roll1, roll2)

        mod = self.modifier(stat, ent)
        if print_results:
            print("{} rolled {} with {} modifier {}".format(ent.get_name(), roll, stat, mod))
        roll += mod
        if print_results:
            print("Result is... {}!!".format(roll))
        return roll

    def passiveCheck(self, stat, ent, advantage=False, disadvantage=False, print_results=True):
        mod = self.modifier(stat, ent)
        roll = 10 + mod
        if advantage:
            roll += 5
        if disadvantage:
            roll -= 5
        if print_results:
            print("Passive Check result w/", stat, "modifier of", mod, ":", roll)
        return roll

    def determineSurprise(self):
        for ent in self.animateList:
            if ent.is_stealthy:
                stealth = self.performCheck("Stealth", ent)
                for ent2 in self.animateList:
                    if type(ent) != type(ent2) and stealth > self.passiveCheck("Perception", ent2, False, False, False):
                        ent2.is_surprised = True

    def resetSurprise(self):
        for ent in self.animateList:
            if ent.is_surprised:
                ent.set_surprise(False)

    # Updated Method
    # ===============================================================================
    def showStats(self) -> None:
        actor = self.currentEntity
        stat = actor.get_stat_block().get_dict()

        print("=============================================================================")
        text = "{:20}".format(actor.get_name())

        if (type(actor) == Player) or (type(actor) == Enemy):
            text += "{:^30}".format(actor.get_race() + " " + actor.get_role()) + "\t[Lv. {:<2}]".format(actor.get_level())
        else:
            text += "{:^30}".format(actor.get_race() + " " + actor.get_role())

        print(text, "\n-----------------------------------------------------------------------------")
        text = "HP: " + "{:12}".format(("{:3} /{}".rjust(12).format(stat["Current HP"], stat["Max HP"])))
        text += "\t" + "{:^30}".format("[AC: {:<2}]".format(stat["Armor Class"]))
        text += "\tSpeed: {:<2}".format(stat["Speed"])
        print(text, "\n=============================================================================")

        if type(actor) == Player and actor.get_companion() is not None:
            print("Companion:", actor.companion)
        elif type(actor) == Enemy:
            print("EXP Yield:", actor.get_exp_yield())

        text = "{:19}".format("Inspiration:") + " {:<2}".format(stat["Inspiration"])
        text += "\t\t{:19}".format("Proficiency Bonus:") + "{:<+2}".format(stat["Proficiency Bonus"]) + "\n"
        print(text)

        tracer, text = 0, ""
        for name, value in list(stat.items())[7:30]:
            if tracer < 6:
                if tracer % 2 == 0:
                    text = "{:19}".format(name + ": ") + "{:2}".format(value)
                else:
                    text += "\t\t{:19}".format(name + ": ") + "{:2}".format(value)
                    print(text)
            elif tracer >= 6:
                if tracer == 6:
                    print()
                if tracer % 3 == 0:
                    text = "{:19}".format(name + ": ") + "{:+2}".format(value)
                else:
                    text += "\t\t{:19}".format(name + ": ") + "{:+2}".format(value)
                    if (tracer + 1) % 3 == 0:
                        print(text)
            tracer += 1

        print("=============================================================================")

    # ===============================================================================
    # Combat Methods
    # ===============================================================================

    def determineInitiative(self):
        order = []
        index = 0
        for ent in self.animateList:
            order.append((index, self.performCheck("Dexterity", ent, False, False, False)))
            index += 1
        order = sorted(order, key=lambda x: - x[1])

        self.animateList[:] = [self.animateList[i[0]] for i in order]

    def next_turn(self):
        self.turnCounter += 1
        self.currentEntity = self.animateList[self.turnCounter % len(self.animateList)]

    def dealDMG(self, damage, target):
        targetHealth = target.get_stat("Current HP")
        targetHealth -= damage
        if targetHealth >= 0:
            target.set_stats("Current HP", targetHealth)
        else:
            target.set_stats("Current HP", 0)

        print(self.currentEntity.get_name(), "attacked", target.get_name(), "!!")
        print(target.get_name(), "took", damage, "damage!!")
        print(target.get_name(), "is now at", target.get_stat("Current HP"), "/",
              target.get_stat("Max HP"), "HP.")

    def attack(self, target, adv, disadv) -> None:
        toHit = target.get_stat("Armor Class")
        attempt = 0

        # if "melee" in self.currentEntity.get_weapon().get_use():
        attempt = self.performCheck("Strength", self.currentEntity, adv, disadv)
        # elif "ranged" in self.currentEntity.get_weapon().get_use():
        #     attempt = self.performCheck("Dexterity", self.currentEntity, adv, disadv)

        if attempt >= toHit:
            damage = self.rollDice(1, 20, False)
            self.dealDMG(damage, target)
        else:
            print("Attack failed!")
