from collections import namedtuple


Recipe = namedtuple(
    "Recipe",
    ("result", "amount", "ingredients", "required_tools"),
    defaults=((),),
)

RECIPES = (
    Recipe("furnace", 1, (("stone", 8),)),
    Recipe("bucket", 1, (("ingot_iron", 3),)),
    Recipe("wrench", 1, (("ingot_copper", 4),)),
    Recipe("clay", 1, (("water", 1), ("sand", 1))),
    Recipe("bonsai_clay", 1, (("clay", 5),)),
    Recipe("crafting_hammer", 1, (("ingot_iron", 3), ("twig", 2))),
    Recipe("crafting_mortar", 1, (("stone", 4), ("twig", 1))),
    Recipe(
        "bronze_plate",
        1,
        (("ingot_bronze", 1),),
        ("crafting_hammer",),
    ),
    Recipe(
        "copper_powder",
        1,
        (("copper_ore", 1),),
        ("crafting_mortar",),
    ),
    Recipe(
        "copper_powder",
        1,
        (("ingot_copper", 1),),
        ("crafting_mortar",),
    ),
    Recipe(
        "tin_powder",
        1,
        (("tin_ore", 1),),
        ("crafting_mortar",),
    ),
    Recipe(
        "tin_powder",
        1,
        (("ingot_tin", 1),),
        ("crafting_mortar",),
    ),
    Recipe(
        "bronze_furnace",
        1,
        (("furnace", 1), ("ingot_bronze", 4)),
    ),
)

ITEM_NAMES = {
    "bonsai": "Bonsai",
    "bonsai_clay": "Unfired Bonsai",
    "bronze_furnace": "Bronze Furnace",
    "bronze_plate": "Bronze Plate",
    "bucket": "Bucket",
    "coal_ore": "Coal Ore",
    "clay": "Clay",
    "copper_ore": "Copper Ore",
    "copper_powder": "Copper Powder",
    "crafting_hammer": "Crafting Hammer",
    "crafting_mortar": "Crafting Mortar",
    "dirt": "Dirt",
    "furnace": "Furnace",
    "glass": "Glass",
    "hemp": "Hemp",
    "ingot_aluminum": "Aluminum Ingot",
    "ingot_bronze": "Bronze Ingot",
    "ingot_chromium": "Chromium Ingot",
    "ingot_copper": "Copper Ingot",
    "ingot_iron": "Iron Ingot",
    "ingot_nickel": "Nickel Ingot",
    "ingot_tin": "Tin Ingot",
    "ingot_steel": "Steel Ingot",
    "iron_ore": "Iron Ore",
    "pickaxe": "Pickaxe",
    "sand": "Sand",
    "sapling": "Sapling",
    "seed": "Seed",
    "stone": "Stone",
    "tin_ore": "Tin Ore",
    "tin_powder": "Tin Powder",
    "twig": "Twig",
    "water": "Water",
    "wrench": "Wrench",
    "wood": "Wood",
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
        and all(
            hotbar is not None and hotbar.count(tool) > 0
            for tool in recipe.required_tools
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
