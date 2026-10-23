from collections import namedtuple


Recipe = namedtuple("Recipe", ("result", "amount", "ingredients"))

RECIPES = (
    Recipe("furnace", 1, (("stone", 8),)),
)

ITEM_NAMES = {
    "dirt": "Dirt",
    "furnace": "Furnace",
    "pickaxe": "Pickaxe",
    "sand": "Sand",
    "stone": "Stone",
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
