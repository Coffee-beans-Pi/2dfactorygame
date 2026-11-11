from item_data import ITEM_PROPERTIES


def grant_debug_items(inventory):
    for item in ITEM_PROPERTIES:
        if item == "pickaxe":
            continue
        inventory.add(item, 1 if item == "wrench" else 30)
