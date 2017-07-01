from collections import defaultdict
from copy import copy


class Contracts(set):
    def __init__(self, name):
        super(Contracts, self).__init__()
        self.name = name
        self._contract_offers_made = {}
        self._contract_requests = defaultdict(list)
        self._contract_offers = defaultdict(list)
        self._contracts_pay = defaultdict(dict)
        self._contracts_deliver = defaultdict(dict)
        self._contracts_payed = []
        self._contracts_delivered = []

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
        self._contract_requests = defaultdict(list)
        self._contract_offers = defaultdict(list)
        self._contracts_payed = []
        self._contracts_delivered = []

        # delete all expired contracts
        for good in self._contracts_deliver:
            for contract in copy(self._contracts_deliver[good]):
                if self._contracts_deliver[good][contract].end_date == round:
                    del self._contracts_deliver[good][contract]

        for good in self._contracts_pay:
            for contract in copy(self._contracts_pay[good]):
                if self._contracts_pay[good][contract].end_date == round:
                    del self._contracts_pay[good][contract]
