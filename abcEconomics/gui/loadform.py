import abcEconomics
from flexx import ui


class LoadForm(ui.Widget):
    def init(self):
        with ui.Widget(style="overflow-y: scroll"):
            with ui.VBox(style="overflow-y: scroll") as self.vbox:
                name_descriptions = [(d['name'], d['description'])
                                     for d in abcEconomics.parameter_database.all()]
                for name, desc in name_descriptions:
                    with ui.GroupWidget():
                        btn = ui.Button(title=name, text=name)
                        delete = ui.Button(title=name, text='(del)')
                        ui.Label(text=desc)

                    btn.connect('mouse_click', self.wdg)
                    delete.connect('mouse_click', self.delete)

    def update(self, event):
        with self.vbox:
            with ui.GroupWidget():
                btn = ui.Button(title=event['name'],
                                text=event['name'])
                delete = ui.Button(title=event['name'], text='del')
                ui.Label(text=event['description'])
            btn.connect('mouse_click', self.wdg)
            delete.connect('mouse_click', self.delete)

    def wdg(self, event):
        self.emit('load', {'name': event['source'].title})

    def delete(self, event):
        abcEconomics.parameter_database.delete(name=event['source'].title)
        event['source'].text = 'deleted'
