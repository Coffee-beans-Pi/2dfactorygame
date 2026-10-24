class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item, amount=1):
        self.items[item] = self.items.get(item, 0) + amount

    def remove(self, item, amount=1):
        if self.items.get(item, 0) < amount:
            return False

        self.items[item] -= amount
        if self.items[item] == 0:
            del self.items[item]
        return True

    def count(self, item):
        return self.items.get(item, 0)


class Hotbar:
    def __init__(self):
        self.slots = [
            "pickaxe", None, None, None, None, None, None, None, None
        ]
        self.counts = [1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.selected_index = 0

    def selected_item(self):
        return self.slots[self.selected_index]

    def add_to_slot(self, index, item, amount=1):
        if not 0 <= index < len(self.slots):
            return False
        if self.slots[index] not in (None, item):
            return False

        self.slots[index] = item
        self.counts[index] += amount
        return True

    def remove_from_slot(self, index, amount):
        if (
            not 0 <= index < len(self.slots)
            or self.slots[index] is None
            or self.counts[index] < amount
        ):
            return None

        item = self.slots[index]
        self.counts[index] -= amount
        if self.counts[index] == 0:
            self.slots[index] = None
        return item

    def set_slot(self, index, item, amount):
        self.slots[index] = item
        self.counts[index] = amount

    def select(self, index):
        if 0 <= index < len(self.slots):
            self.selected_index = index
