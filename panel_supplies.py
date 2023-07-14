from panel import KMiffedPanel

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label

class PanelSupplies(KMiffedPanel):
    #
    # Types
    #
    class SetDataMsg(Message):
        """Set widget data message."""
        def __init__(self,
                     water: float,
                     water_max: float,
                     food: float,
                     food_max: float,
                     oxygen: float,
                     oxygen_max: float,
                     atmo: float,
                     atmo_max: float,
                     waste_atmo: float,
                     waste_atmo_max: float) -> None:
            self.water = water
            self.water_max = water_max
            self.food = food
            self.food_max = food_max
            self.oxygen = oxygen
            self.oxygen_max = oxygen_max
            self.atmo = atmo
            self.atmo_max = atmo_max
            self.waste_atmo = waste_atmo
            self.waste_atmo_max = waste_atmo_max
            super().__init__()

    #
    # Constructor
    #
    def __init__(self, classes="", id=""):
        super().__init__("Supplies", classes=classes, id=id)

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        yield Label("Water", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-supplies-water")
        yield Label("Food", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-supplies-food")
        yield Label("Oxygen", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-supplies-oxygen")
        yield Label("Atmosphere", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-supplies-atmo")
        yield Label("WasteAtmosphere", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-supplies-waste-atmo")

    def set_data(self,
                 water: float,
                 water_max: float,
                 food: float,
                 food_max: float,
                 oxygen: float,
                 oxygen_max: float,
                 atmo: float,
                 atmo_max: float,
                 waste_atmo: float,
                 waste_atmo_max: float) -> None:
        water_pct = (water / water_max * 100.0) if (water_max > 0) else 0
        food_pct = (food / food_max * 100.0) if (food_max > 0) else 0
        oxygen_pct = (oxygen / oxygen_max * 100.0) if (oxygen_max > 0) else 0
        atmo_pct = (atmo / atmo_max * 100.0) if (atmo_max > 0) else 0
        waste_atmo_pct = (waste_atmo / waste_atmo_max * 100.0) if (waste_atmo_max > 0) else 0
        self.label_water.update("{:6.1f} / {:6.1f}   {:3.0f}%".format(water, water_max, water_pct))
        self.label_food.update("{:6.1f} / {:6.1f}   {:3.0f}%".format(food, food_max, food_pct))
        self.label_oxygen.update("{:6.1f} / {:6.1f}   {:3.0f}%".format(oxygen, oxygen_max, oxygen_pct))
        self.label_atmo.update("{:6.1f} / {:6.1f}   {:3.0f}%".format(atmo, atmo_max, atmo_pct))
        self.label_waste_atmo.update("{:6.1f} / {:6.1f}   {:5.1f}%".format(waste_atmo, waste_atmo_max, waste_atmo_pct))

    #
    # Event Handlers
    #
    def on_mount(self) -> None:
        # assign title to panel
        self.border_title = self.PANEL_TITLE

        # store frequently used widgets
        self.label_water = self.query_one("#field-value-supplies-water", Label)
        self.label_food = self.query_one("#field-value-supplies-food", Label)
        self.label_oxygen = self.query_one("#field-value-supplies-oxygen", Label)
        self.label_atmo = self.query_one("#field-value-supplies-atmo", Label)
        self.label_waste_atmo = self.query_one("#field-value-supplies-waste-atmo", Label)

    #
    # Message Handlers
    #
    def on_panel_supplies_set_data_msg(self, message: SetDataMsg) -> None:
        self.set_data(
            message.water,
            message.water_max,
            message.food,
            message.food_max,
            message.oxygen,
            message.oxygen_max,
            message.atmo,
            message.atmo_max,
            message.waste_atmo,
            message.waste_atmo_max)
