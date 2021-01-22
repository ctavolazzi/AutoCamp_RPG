
from entity import Entity
from statblock import StatBlock
import random


class Animate(Entity):
    def __init__(self, name, entity_id, race, role, level, stat_block=StatBlock()):
        super().__init__(name, entity_id)       # should inherit everything this way
        self.conditions = set()

        self.stat_block = stat_block
        self.race = race
        self.role = role
        self.level = level
        self.inventory = dict()                 # Key is Item, Value is quantity.
        self.inv_max = 20                       # maximum inventory capacity possible
        self.inv_scheme = "slot"                # whether the inventory stores by slot, item weight, or infinite
        self.is_enemy = None
        self.is_stealthy = False
        self.is_surprised = False

    # ==================================
    # Inventory
    # ==================================





    # ==================================
    # Accessors
    # ==================================
    def get_stat_block(self):
        return self.stat_block

    def get_level(self):
        return self.level

    def get_role(self):
        return self.role

    def get_race(self):
        return self.race

    def get_stat(self, stat):
        return self.stat_block.get_stat(stat)

    def get_conditions(self):
        return self.conditions

    def get_iff(self):
        return self.is_enemy

    def get_inv_max(self):
        return self.inv_max

    def get_inv_scheme(self):
        return self.inv_scheme

    # ==================================
    # Mutators
    # ==================================
    def level_up(self):
        if self.level < 20:
            self.level += 1
            new_hp = random.randint(1, self.stat_block.get_stat("Hit Dice"))
            old_hp = self.stat_block.get_stat("Max HP")
            self.stat_block.modify_stat("Max HP", old_hp + new_hp)
            self.stat_block.modify_stat("Current HP", old_hp + new_hp)
            print("[OK] Level Updated to ", self.level, "!")
        else:
            print("[ER] Already at max level!")

    def mod_level(self, value):
        if (value > 0) and (value < 21):
            self.level = value
            print("[OK] Level Updated to ", value, "!")
        else:
            print("[ER] Invalid Level!")

    def mod_role(self, role):
        self.role = role

    def mod_race(self, race):
        self.race = race

    def set_stats(self, stat, num):
        self.stat_block.modify_stat(stat, num)

    def mod_conditions(self, add, cond):  # True if adding, False if removing
        validCond = ("blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated", "invisible",
                     "paralyzed", "petrified", "poisoned", "prone", "restrained", "stunned", "unconscious")
        if cond.lower() in validCond:
            if add:
                self.conditions.add(cond.lower())
            else:
                self.conditions.remove(cond)
        else:
            print(cond + " is not a valid condition!!")

    def set_surprise(self, surprise_status):
        self.is_surprised = surprise_status

    def set_stealth(self, stealth_status):
        self.is_stealthy = stealth_status

    def set_iff(self, iff):
        self.is_enemy = iff

    def set_inv_scheme(self, scheme=None):
        if scheme == "slot" or scheme == "weight" or scheme is None:
            self.inv_scheme = scheme
        else:
            print("[ER] Invalid inventory scheme!")

    def set_inv_max_size(self, size):
        self.inv_max = size


