from collections import namedtuple


Recipe = namedtuple("Recipe", ("result", "amount", "ingredients"))

RECIPES = (
    Recipe("furnace", 1, (("stone", 8),)),
)

ITEM_NAMES = {
    "coal_ore": "Coal Ore",
    "copper_ore": "Copper Ore",
    "dirt": "Dirt",
    "furnace": "Furnace",
    "iron_ore": "Iron Ore",
    "pickaxe": "Pickaxe",
    "sand": "Sand",
    "sapling": "Sapling",
    "seed": "Seed",
    "stone": "Stone",
    "tin_ore": "Tin Ore",
    "twig": "Twig",
}


def get_craftable_recipes(inventory):
    return [
        recipe
        for recipe in RECIPES
        if all(
            inventory.count(item) >= amount
            for item, amount in recipe.ingredients
        )
    ]


def craft_recipe(inventory, recipe):
    if recipe not in get_craftable_recipes(inventory):
        return False

    for item, amount in recipe.ingredients:
        inventory.remove(item, amount)
    inventory.add(recipe.result, recipe.amount)
    return True
