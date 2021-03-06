# This file is part of Foshelter, see <https://github.com/MestreLion/foshelter>
# Copyright (C) 2018 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>

"""
    Top level game classes
"""

import json

from . import orm
from . import dwellers
from . import savefile
from . import util




class LunchBox(util.FSEnum):
    REGULAR           = 0
    MR_HANDY          = 1
    PET_CARRIER       = 2
    STARTER_PACK      = 3
    NUKA_COLA_QUANTUM = 4


class LunchBoxes(orm.EntityList):
    EntityClass = LunchBox

    def __delitem__(self, key):
        super().__delitem__(key)
        self._root.update_lunchboxes()

    def insert(self, idx: int, obj: LunchBox):
        super().insert(idx, obj)
        self._root.update_lunchboxes()


class Game(orm.RootEntity):
    """Root class for a game save"""

    @classmethod
    def from_save(cls, path: str, decrypted: bool = False):
        with open(path, 'r') as fd:
            data = fd.read()

        if decrypted:
            try:
                return cls.from_data(savefile.decode(data))
            except json.decoder.JSONDecodeError as e:
                raise util.FSException('Could not load Vault data,'
                   ' is it a decrypted JSON file? %s: %s', path, e)

        try:
            return cls.from_data(savefile.decrypt(data))
        except ValueError as e:
            raise util.FSException('Could not load Vault data,'
               ' is it an encrypted SAV file? %s: %s', path, e)


    def __init__(self, data: dict):
        super().__init__(data)

        self.dwellers = dwellers.Dwellers(data['dwellers']['dwellers'], self)
        self.lunchboxes = LunchBoxes(data["vault"]["LunchBoxesByType"], self)


    def to_save(self, path:str, decrypted=False, pretty=False, sort=False):
        if decrypted:
            data = savefile.encode(self.to_data(), pretty, sort)
            with open(path, 'w') as fd:
                fd.write(data)
                return

        data = savefile.encrypt(self.to_data())
        with open(path, 'wb') as fd:
            fd.write(data)


    def update_lunchboxes(self):
        count = len(self.lunchboxes)
        self._data["vault"]["LunchBoxesCount"] = count
