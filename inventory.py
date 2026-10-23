class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item, amount=1):
        self.items[item] = self.items.get(item, 0) + amount

    def remove(self, item, amount=1):
        if self.items.get(item, 0) < amount:
            return False

        self.items[item] -= amount
        return True

    def count(self, item):
        return self.items.get(item, 0)


class Hotbar:
    def __init__(self):
        self.slots = [
            "pickaxe", None, None, None, None, None, None, None, None, None
        ]
        self.selected_index = 0

    def selected_item(self):
        return self.slots[self.selected_index]

    def select(self, index):
        if 0 <= index < len(self.slots):
            self.selected_index = index
