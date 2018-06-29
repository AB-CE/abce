from flexx.pyscript import window
from flexx.ui import Layout
from flexx import event


class DockPanel(Layout):
    """ A layout that displays its children as dockable widgets.

    This is a high level layout allowing the user to layout the child
    widgets as he/she likes. The title of each child is used for its
    corresponding tab label.

    the widget's style property 'location' determines where to place the
    next new widget.

    location = N, S, W, or E:
        for absolute placement.
    location = L(eft), R(ight), U(nder), O(ver) B(efore) A(fter):
        for relative placement.
    relative:
        Relative to the last widget or to the widget set with set_relative
    """

    CSS = """

    div.p-TabBar {
        border: 1px solid #ccc;
        width: 20% !important;
        height: 100% !important;
        overflow-y: scroll;
        border-color: steelblue !important;
    }

    div.p-TabBar-body {
        border-color: steelblue !important;
    }

    ul.p-TabBar-content {
    display: block  !important;
        background-color: steelblue !important;
    }

    span.p-TabBar-tabText {
        color: white !important;
    }

    span.p-TabBar-tabText:hover {
        color: steelblack !important;
    }

    li.p-TabBar-tab {
        border-color: steelblue !important;
        background-color: steelblue !important;
    }

    li.p-TabBar-tab:hover {
        border-color: black !important;
        border: 2px solid #ccc;
        background-color: DodgerBlue !important;
    }

    li.p-mod-current {
        background-color: DodgerBlue  !important;
    }
    div.p-TabBar-tab button {
        display: block  !important;
        background-color: red !important;
        color: black;
        padding: 22px 16px;
        width: 20% !important;
        border: none;
        outline: none;
        text-align: left !important;
        cursor: pointer !important;
        transition: 0.3s;
    }

    div.p-StackedPanel {
        top: 0px !important;
        padding: 0px 12px;
        border: 1px solid #ccc;
        width: 80% !important;
        border-left: none !important;
        left: 20% !important;
        height: 100% !important;
    }
    """

    def selectWidget(self, widget):
        self.emit('myselectWidget', {'widget': widget})

    class Both:

        def set_relative(self, widget):
            """ The next attached widget will be placed relative to
            this one """
            self.relative = widget.phosphor

    class JS:
        @event.connect('myselectWidget')
        def myselectWidget(self, event):
            self.phosphor.selectWidget(event['widget'].phosphor)

        def _init_phosphor_and_node(self):
            self.phosphor = window.phosphor.dockpanel.DockPanel()
            self.node = self.phosphor.node
            self.relative = None

        def _add_child(self, widget):
            after = widget.style.split('location:')[1]
            try:
                location = after.split(';')[0]
            except TypeError:
                location = ""
            location = location.upper()
            if 'W' in location:
                self.phosphor.insertLeft(widget.phosphor)
            elif 'N' in location:
                self.phosphor.insertTop(widget.phosphor)
            elif 'E' in location:
                self.phosphor.insertRight(widget.phosphor)
            elif 'S' in location:
                self.phosphor.insertBottom(widget.phosphor)
            else:
                if self.relative is None:
                    self.phosphor.insertLeft(widget.phosphor)
                elif 'L' in location:
                    try:
                        self.phosphor.insertLeft(widget.phosphor,
                                                 self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertLeft(widget.phosphor,
                                                 self.lastworking)

                elif 'O' in location:
                    try:
                        self.phosphor.insertTop(widget.phosphor,
                                                self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertTop(widget.phosphor,
                                                self.lastworking)

                elif 'R' in location:
                    try:
                        self.phosphor.insertRight(widget.phosphor,
                                                  self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertRight(widget.phosphor,
                                                  self.lastworking)

                elif 'U' in location:
                    try:
                        self.phosphor.insertBottom(widget.phosphor,
                                                   self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertBottom(widget.phosphor,
                                                   self.lastworking)

                elif 'B' in location:
                    try:
                        self.phosphor.insertTabBefore(widget.phosphor,
                                                      self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertTabBefore(widget.phosphor,
                                                      self.lastworking)

                elif 'A' in location:
                    try:
                        self.phosphor.insertTabAfter(widget.phosphor,
                                                     self.relative)
                        self.lastworking = self.relative
                    except Exception:
                        self.phosphor.insertTabAfter(widget.phosphor,
                                                     self.lastworking)

                else:
                    self.phosphor.insertLeft(widget.phosphor)
            self.relative = widget.phosphor
