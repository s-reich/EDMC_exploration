# global symbols used for placement etc.
import random

E = 'e'
W = 'w'
LEFT = 'l'
CENTER = 'c'
RIGHT = 'r'

# nice color map: https://cs111.wellesley.edu/archive/cs111_fall14/public_html/labs/lab12/tkintercolor.html

class Widget:
    def __init__(self, parent: 'Widget|None' = None):
        self.parent: Widget|None = parent
        self.children: list[Widget] = []
        if parent:
            parent.add_child(self)

    def destroy(self, call_parent: bool = True):
        # print(f"Destroy widget {self}")
        for c in self.children:
            c.destroy(call_parent=False)
        self.children.clear()
        if self.parent and call_parent:
            self.parent.remove_child(self)

    def add_child(self, child: 'Widget') -> None:
        self.children.append(child)

    def remove_child(self, child: 'Widget') -> None:
        self.children.remove(child)

    def winfo_children(self) -> list['Widget']:
        # need a copy so we can modify while iterating
        return list(self.children)

    def print_recursive(self, indent: int = 0) -> None:
        print((' '*indent) + f'{self}:')
        for c in self.children:
            c.print_recursive(indent + 2)


class Frame(Widget):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        self.grid: dict[int, dict[int, Widget]] = {}

    def set_grid(self, element: Widget, row: int, column: int, _sticky: str) -> None:
        # assert element in self.children
        if row not in self.grid:
            self.grid[row] = {column: element}
        self.grid[row][column] = element

    def print_recursive(self, indent: int = 0) -> None:
        if not self.grid:
            super().print_recursive(indent)
            return
        print((' '*indent) + f'{self} GRID:')
        for r in sorted(self.grid):
            data: dict[int, Widget] = self.grid[r]
            txt: str = ' '*(indent+4) + f'{r}: '
            txt += " | ".join(
                [str(data[c]) for c in sorted(data)]
            )
            print(txt)

    def remove_child(self, child: 'Widget') -> None:
        for ri, rd in self.grid.items():
            for ci, cd in rd.items():
                if cd == child:
                    rd.pop(ci)
                    break
            if not rd:
                self.grid.pop(ri)
                break
        super().remove_child(child)


class Label(Widget):
    # self.tk_frame, text=f'[{body_name}]: ', justify=tk.RIGHT)
    def __init__(self, parent: Widget, text: str, justify: str = CENTER, fg: str = 'd', font: str = 'd'):
        super().__init__(parent)
        self.text: str = text
        self.justify: str = justify
        self.fg: str = fg
        self.font: str = font

    def __str__(self) -> str:
        return f'{self.text} [[{self.justify}, {self.fg}, {self.font}]]'

    def grid(self, row: int, column: int, sticky: str = W) -> None:
        assert isinstance(self.parent,Frame)
        self.parent.set_grid(self, row, column, sticky)


if __name__ == '__main__':
    from scanresult import *

    # short printing test
    master: Widget = Widget()
    tk_frame = Frame(master)
    master.print_recursive()
    print('-'*20)

    for w in tk_frame.winfo_children():
        w.destroy()
    master.print_recursive()
    print('-'*20)

    for row in range(4):
        p_name = Label(tk_frame, text=f'[body {row}]: ', justify=RIGHT)
        p_name.grid(row=row, column=0, sticky=W)

        symbol: str = 'X'*row
        p_symbol = Label(tk_frame, text=symbol, justify=CENTER)
        p_symbol.grid(row=row, column=1, sticky=W)

        col: int = 2
        for scan_result in [
            ScanResult(1),
            ScanWithShipOrSuit('Little Dipper'),
            ScanFromOrbit('Tussock', {}),
            ScanWithShipOrSuit('Bacterium Verrata')
        ]:
            color: str = scan_result.get_display_color()
            text: str = scan_result.get_display_string()
            label_props: dict = {
                "text": text,
                "justify": LEFT,
                "fg": color
            }
            if scan_result.is_done():
                label_props['font'] = "-weight bold"

            p_desc = Label(tk_frame, **label_props)
            p_desc.grid(row=row, column=col, sticky=W)
            col += 1

    master.print_recursive()
    print('-'*20)

    for w in tk_frame.winfo_children():
        w.destroy()
    master.print_recursive()
    print('-'*20)
