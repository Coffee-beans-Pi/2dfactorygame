from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ItemProperties:
    burnable: bool = False
    smeltable: bool = False
    smelt_result: Optional[str] = None


_ITEM_IDS = (
    "pickaxe",
    "dirt",
    "stone",
    "sand",
    "sapling",
    "seed",
    "twig",
    "coal_ore",
    "iron_ore",
    "copper_ore",
    "tin_ore",
    "furnace",
    "bonsai_clay",
    "bonsai",
    "hemp",
    "bucket",
    "clay",
    "glass",
    "ingot_aluminum",
    "ingot_bronze",
    "ingot_chromium",
    "ingot_copper",
    "ingot_iron",
    "ingot_nickel",
    "ingot_tin",
    "wrench",
    "water",
    "wood",
)

ITEM_PROPERTIES = {item: ItemProperties() for item in _ITEM_IDS}
ITEM_PROPERTIES.update({
    "coal_ore": ItemProperties(burnable=True),
    "sapling": ItemProperties(burnable=True),
    "sand": ItemProperties(smeltable=True, smelt_result="glass"),
    "bonsai_clay": ItemProperties(smeltable=True, smelt_result="bonsai"),
    "iron_ore": ItemProperties(smeltable=True, smelt_result="ingot_iron"),
    "copper_ore": ItemProperties(smeltable=True, smelt_result="ingot_copper"),
    "tin_ore": ItemProperties(smeltable=True, smelt_result="ingot_tin"),
})

DEFAULT_ITEM_PROPERTIES = ItemProperties()


def get_item_properties(item):
    return ITEM_PROPERTIES.get(item, DEFAULT_ITEM_PROPERTIES)
