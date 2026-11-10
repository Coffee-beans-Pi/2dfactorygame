from collections import namedtuple


Recipe = namedtuple("Recipe", ("result", "amount", "ingredients"))

RECIPES = (
    Recipe("furnace", 1, (("stone", 8),)),
)

ITEM_NAMES = {
    "bonsai": "Bonsai",
    "bonsai_clay": "Bonsai Clay",
    "bucket": "Bucket",
    "coal_ore": "Coal Ore",
    "clay": "Clay",
    "copper_ore": "Copper Ore",
    "dirt": "Dirt",
    "furnace": "Furnace",
    "glass": "Glass",
    "ingot_aluminum": "Aluminum Ingot",
    "ingot_bronze": "Bronze Ingot",
    "ingot_chromium": "Chromium Ingot",
    "ingot_copper": "Copper Ingot",
    "ingot_iron": "Iron Ingot",
    "ingot_nickel": "Nickel Ingot",
    "ingot_tin": "Tin Ingot",
    "iron_ore": "Iron Ore",
    "pickaxe": "Pickaxe",
    "raw_copper": "Raw Copper",
    "raw_iron": "Raw Iron",
    "raw_tin": "Raw Tin",
    "sand": "Sand",
    "sapling": "Sapling",
    "seed": "Seed",
    "stone": "Stone",
    "tin_ore": "Tin Ore",
    "twig": "Twig",
    "water": "Water",
}


def get_craftable_recipes(inventory, hotbar=None):
    return [
        recipe
        for recipe in RECIPES
        if all(
            inventory.count(item)
            + (hotbar.count(item) if hotbar is not None else 0)
            >= amount
            for item, amount in recipe.ingredients
        )
    ]


def craft_recipe(inventory, recipe, hotbar=None):
    if recipe not in get_craftable_recipes(inventory, hotbar):
        return False

    for item, amount in recipe.ingredients:
        inventory_amount = min(inventory.count(item), amount)
        if inventory_amount:
            inventory.remove(item, inventory_amount)
        remaining = amount - inventory_amount
        if remaining and hotbar is not None:
            hotbar.remove(item, remaining)
    inventory.add(recipe.result, recipe.amount)
    return True
