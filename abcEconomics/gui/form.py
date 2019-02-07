"""Form to input parameters acording to the parameter_mask"""
import abcEconomics
from flexx import ui, event


def form(parameter_mask, names):
    """Gererates Form class instance with parameter_mask and names"""
    class Form(ui.Widget):
        def init(self):
            self.fields = {}
            self.radio_buttons = {}
            self.result_property = {}
            self.slider_to_textfield = {}
            self.textfield_to_slider = {}
            self.int_sliders = set()
            self.sliders = []

            with ui.GroupWidget(title="Simulation parameter"):
                ui.Label(text="scroll down to start",
                         style="float: right; color: steelblue", wrap=True)
                for parameter, value in list(parameter_mask.items()):
                    try:
                        title = names[parameter]
                    except KeyError:
                        title = parameter

                    if isinstance(value, bool):
                        self.fields[parameter] = ui.CheckBox(text=title)
                        self.result_property[parameter] = 'checked'

                    elif isinstance(value, list):
                        self.radio_buttons[parameter] = {}
                        with ui.GroupWidget(title=title,
                                            style="width:fit-content;"):
                            for option in value:
                                self.radio_buttons[parameter][option] = \
                                    ui.RadioButton(text=option)
                        self.radio_buttons[parameter][value[0]].checked = True

                    else:
                        if isinstance(value, tuple):
                            min_value, default, max_value = sorted(value)
                        elif isinstance(value, (int, float)):
                            min_value, default, max_value = 0, value, value * 2

                        is_integer = False
                        if isinstance(value, (int, float, tuple)):
                            if (isinstance(default, int) and
                                    isinstance(max_value, int)):
                                step = 1
                                is_integer = True
                                # if default is float, type is float
                                if isinstance(default, float):
                                    step = (max_value - min_value) / 100
                            else:
                                step = (max_value - min_value) / 100
                            with ui.Widget():
                                ui.Label(text=title, wrap=True)
                                slider = ui.Slider(min=min_value,
                                                   max=max_value,
                                                   value=default,
                                                   step=step)
                                lineeditor = ui.LineEdit(title=title,
                                                         text=default)
                                self.sliders.append((slider, lineeditor))
                            self.fields[parameter] = slider
                            self.result_property[parameter] = 'value'
                            slider.connect('value', self.stt)
                            lineeditor.connect('submit', self.tts)
                            self.slider_to_textfield[slider] = lineeditor
                            self.textfield_to_slider[lineeditor] = slider
                            if is_integer:
                                self.int_sliders.add(slider)

                        elif isinstance(value, str):
                            with ui.Widget():
                                ui.Label(text=title,
                                         wrap=True, style="width: 80%")
                                self.fields[parameter] = \
                                    ui.LineEdit(title=title,
                                                text=value,
                                                style='width: 95%;')
                            self.result_property[parameter] = 'text'
                        elif value is None:
                            ui.Label(text=title, wrap=True)
                        else:  # field
                            print(str(value) + "not recognized")
                with ui.VBox():
                    self.btn = ui.Button(text="start simulation")
                with ui.GroupWidget(title="Save"):
                    with ui.HBox():
                        self.name = ui.LineEdit(title="Name:",
                                                placeholder_text='name')
                        self.save = ui.Button(text="Save Parameters")
                    self.description = ui.LineEdit(
                        title="Description",
                        text='',
                        style='width: 95%;',
                        placeholder_text='description')

        def parse_parameter(self):
            parameter = {}
            for key, element in self.fields.items():
                parameter[key] = getattr(element,
                                         self.result_property[key])
                if element in self.int_sliders:
                    parameter[key] = int(parameter[key])
            for parameter, group in self.radio_buttons.items():
                for value, checkbox in group.items():
                    if checkbox.checked:
                        parameter[parameter] = value
            return parameter

        @event.connect('save.mouse_click')
        def _save(self, events):
            parameter = self.parse_parameter()
            parameter['name'] = self.name.text
            parameter['description'] = self.description.text
            abcEconomics.parameter_database.upsert(parameter, keys=['name'])
            self.emit('update_parameter_database', parameter)

        def load_parameter(self, event):
            parameter = abcEconomics.parameter_database.find_one(name=event['name'])

            for key, element in self.fields.items():
                if isinstance(element, ui.CheckBox):
                    element.checked = parameter[key]
                elif isinstance(element, ui.LineEdit):
                    element.text = parameter[key]
                elif isinstance(element, ui.Slider):
                    element.value = parameter[key]
                    self.slider_to_textfield[element].text = parameter[key]

            for parameter, group in self.radio_buttons.items():
                for value, checkbox in group.items():
                    checkbox.checked = bool(parameter[parameter] == value)
            return parameter

        @event.connect('btn.mouse_click')
        def wdg(self, *event):
            parameter = self.parse_parameter()
            self.emit('run_simulation',
                      {'simulation_parameter': parameter})

        def stt(self, events):
            # This is executed in python, but should
            # be executed in JS without server interaction
            slider = events['source']
            if slider in self.int_sliders:
                self.slider_to_textfield[slider].text = int(
                    events['new_value'])
            else:
                self.slider_to_textfield[slider].text = float(
                    events['new_value'])

        def tts(self, events):
            # This is executed in python, but should
            # be executed in JS without serve interaction
            slider = self.textfield_to_slider[events['source']]
            if slider in self.int_sliders:
                new_value = int(events['source'].text)
            else:
                new_value = float(events['source'].text)
            if new_value > slider.max:
                slider.max = new_value
            if new_value < slider.min:
                slider.min = new_value
            slider.value = new_value

    return Form


def assert_all_of_the_same_type(values):
    for item in values:
        if isinstance(item, type(values[0])):
            raise ValueError("all list values must be of the same type. "
                             "If 5.5 is used 0.0 instead of 0 must be used: " +
                             str(values))
