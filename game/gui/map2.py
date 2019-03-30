import pride.components.base
import pride.gui.gui

EARTH_COLOR = (155, 125, 55, 255)

class Base_Cell(pride.components.base.Base):

    mutable_defaults = {"cells" : list}

    def process_neighbor(self, neighbor):
        pass


class World_Cell(Base_Cell):

    defaults = {"selector" : 0}
    mutable_defaults = {"light_value" : lambda: [0, 0], "water_value" : lambda: [0, 0],
                        "elevation_value" : lambda: [0, 0]}

    def process_neighbor(self, neighbor):
        selector = self._selector ^ 1
        self.light_value[selector] = self.process_light(neighbor)
        self.water_value[selector] = self.process_water(neighbor)
        self.elevation_value[selector] = self.process_elevation(neighbor)
        self.selector ^= 1

    def process_light(self, neighbor):
        return self.light_value[self.selector] # do nothing stub for now

    def process_water(self, neighbor):
        return self.water_value[self.selector]

    def process_elevation(self, neighbor):
        return self.elevation_value[self.selector]


class CA_World(pride.components.base.Base):

    defaults = {"columns" : 10, "rows" : 10, "priority" : .04, "cell_type" : World_Cell}
    verbosity = {"setup_cells" : "vv"}
    post_initializer = "setup_cells"

    def _get_grid_size(self):
        return (self.columns, self.rows)

    def setup_cells(self):
        self.alert("Setting up {} by {} grid".format(*self.grid_size), level=self.verbosity["setup_cells"])
        Cell = self.cell_type
        cells = self.cells = [[Cell() for column_i in range(self.column)] for row_i in range(self.rows)]
        for row in range(self.rows):
            for column in range(self.columns):
                cell = cells[column][row]

                for _index in range(-1, 2):
                    for _index2 in range(-1, 2):
                        _column, _row = column + _index, row + _index2
                        if _row < 0 or _column < 0 or (_column, _row) == (column, row):
                            continue
                        try:
                            neighbor = cells[_column][_row]
                        except IndexError:
                            pass
                        else:
                            cell.neighbors.append(neighbor)
        instruction = pride.Instruction(self.reference, "process_grid")
        self.instruction = instruction
        instruction.execute(priority=self.priority)

    def process_grid(self):
        for row in self.cells:
            for cell in row:
                for neighbor in cell.neighbors:
                    cell.process_neighbor(neighbor)
        self.instruction.execute(priority=self.priority)


class Cell_Theme(pride.gui.gui.Theme):

    def draw_texture(self):
        area = self.area
        self.draw("fill", area, color=EARTH_COLOR)
        self.draw("rect_width", area, color=self.color, width=self.outline_width)


class Cell_View(pride.gui.gui.Button):

    defaults = {"cell" : None, "theme_type" : Cell_Theme}
    required_attributes = ("cell", )


class World_View(pride.gui.gui.Window):

    defaults = {"ca_world" : None}
    post_initializer = "setup_grid"

    def setup_grid(self):
        ca_world = self.ca_world
        for row_index, row in enumerate(ca_world.cells):
            container = self.create("pride.gui.gui.Container", pack_mode="top")
            for cell_index, cell in row:
                container.create(Cell_View(cell))

class Game_World(pride.gui.gui.Window):

    post_initializer = "create_world"

    def create_world(self):
        ca_world = self.create(Ca_World)
        world_view =
