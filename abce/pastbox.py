class Postbox:
    def __init__(self):
        self.boxes = {}

    def get(self, name):
        ret = self.boxes[name]
        self.boxes[name] = []
        return ret

    def post(self, name, message):
        try:
            self.boxes[name].append(message)
        except KeyError:
            self.boxes[name] = [message]
