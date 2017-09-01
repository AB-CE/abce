from copy import copy


class Contracts(set):
    def __init__(self, par=set()):
        super(Contracts, self).__init__(par)

    def add(self, entry):
        assert entry not in self
        super().add(entry)

    def remove(self, entry):
        super().remove(entry)

    def possessions(self):
        return copy(self)

    def possession(self, typ):
        ret = set()
        for contract in self:
            if isinstance(contract, typ):
                ret.add(contract)
        return ret

    def calculate_netvalue(self, parameters, value_functions):
        return sum(value_functions[entry.__class__](entry, parameters)
                   for entry in self)

    def calculate_assetvalue(self, parameters, value_functions):
        return sum(max(value_functions[entry.__class__](entry, parameters), 0)
                   for entry in self)

    def calculate_liablityvalue(self, parameters, value_functions):
        return sum(min(value_functions[entry.__class__](entry, parameters), 0)
                   for entry in self)

    def calculate_valued_assets(self, parameters, value_functions):
        ret = {str(entry): value_functions[entry.__class__](entry, parameters)
               for entry in self
               if value_functions[entry.__class__](entry, parameters) >= 0}
        return ret

    def calculate_valued_liablities(self, parameters, value_functions):
        ret = {str(entry): value_functions[entry.__class__](entry, parameters)
               for entry in self
               if value_functions[entry.__class__](entry, parameters) < 0}
        return ret

    # contracts
    def _advance_round(self, round):
        du = set(filter(lambda c: c.terminated, self))
        self.difference_update(du)
