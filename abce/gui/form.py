from flexx import ui, event


def form(parameters, names):
    class Form(ui.Widget):
        def init(self):
            self.fields = {}
            self.radio_buttons = {}
            self.result_property = {}
            self.slider_to_textfield = {}
            self.textfield_to_slider = {}
            self.int_sliders = set()
            self.sliders = []

            for parameter, value in list(parameters.items()):
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
                        if (isinstance(default, int)
                                and isinstance(max_value, int)):
                            step = 1
                            is_integer = True
                            # if default is float, type is float
                            if isinstance(default, float):
                                step = 1.
                        else:
                            step = (max_value - min_value) / 100
                        with ui.Widget():
                            ui.Label(text=title, wrap=True)
                            s = ui.Slider(min=min_value, max=max_value,
                                          value=default, step=step)
                            f = ui.LineEdit(title=title, text=default)
                            self.sliders.append((s, f))
                        self.fields[parameter] = s
                        self.result_property[parameter] = 'value'
                        s.connect('value', self.stt)
                        f.connect('submit', self.tts)
                        self.slider_to_textfield[s] = f
                        self.textfield_to_slider[f] = s
                        if is_integer:
                            self.int_sliders.add(s)

                    elif isinstance(value, str):
                        with ui.Widget():
                            ui.Label(text=title, wrap=True)
                            self.fields[parameter] = \
                                ui.LineEdit(title=title,
                                            text=value,
                                            style='width: 95%;')
                        self.result_property[parameter] = 'text'
                    elif value is None:
                        ui.Label(text=title, wrap=True)
                    else:  # field
                        raise Exception(str(value) + "not recognized")

            self.btn = ui.Button(text="start")

        @event.connect('btn.mouse_click')
        def wdg(self, *event):
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
            self.emit('run_simulation',
                      {'simulation_parameter': parameter})

        class Both:

            def stt(self, event):  # This is executed in python, but should
                            # be executed in JS without server interaction
                slider = event['source']
                if slider in self.int_sliders:
                    self.slider_to_textfield[slider].text = int(
                        event['new_value'])
                else:
                    self.slider_to_textfield[slider].text = float(
                        event['new_value'])

            def tts(self, event):  # This is executed in python, but should
                            # be executed in JS without serve interaction
                slider = self.textfield_to_slider[event['source']]
                if slider in self.int_sliders:
                    new_value = int(event['source'].text)
                else:
                    new_value = float(event['source'].text)
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
                             "If 5.5 is used 0.0 instead of 0 must be used: "
                             + str(values))
