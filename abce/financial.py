class Credit:
    def __init__(self, lender, borrower, amount, interest, issued):
        self.lender = lender
        self.borrower = borrower
        self.amount = amount
        self.interest = interest
        self.issued = issued


class Financial:
    def __init__(self):
        self.assets = {}
        self.liabilities = {}

    def request_credit(self, receiver_group, receiver_id, amount):
        credit_request = Credit((receiver_group, receiver_id)
                                (self.group, self.id),
                                amount,
                                None,
                                None)
        self.message(receiver_group, receiver_id, _cr, credit_request)

    def get_credit_requests(self):
        return self.get_messages('_cr')

    def offer_credit(self, credit_request, interest_rate):
        credit_request.interest = interest_rate

    def accept_credit(self, credit_request):
        pass
