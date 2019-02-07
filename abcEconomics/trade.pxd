import cython

cdef double epsilon
cdef double fmax(double a, double b)
cdef class Offer:
    cdef readonly object sender, receiver
    cdef readonly str good, currency
    cdef readonly double quantity, price
    cdef readonly bint sell
    cdef public str status
    cdef public double final_quantity
    cdef readonly long id
    cdef readonly int made
    cdef public int status_round
    # __init__(self, object sender, object receiver, object good, double quantity, double price, str currency,
    #          bint sell, str status, double final_quantity, long id,
    #          int made, int status_round)

#cpdef Offer rebuild_offer(object sender, object receiver, object good, double quantity, double price,
#                  str currency, bint sell, str status, double final_quantity,
#                  long id, int made, int status_round)

cdef class Trade:
    @cython.locals(available = double, offer = Offer)
    cpdef Offer sell(self, object receiver,
               object good, double quantity, double price, str currency=*, double epsilon=*)
    @cython.locals(available = double, money_amount = double, offer = Offer)
    cpdef Offer buy(self, object receiver, object good,
              double quantity, double price, str currency=*, double epsilon=*)
    @cython.locals(money_amount = double, offer_quantity = double, available = double)
    cpdef object accept(self, Offer offer, double quantity=*, double epsilon=*)
    @cython.locals(offer = Offer)
    cpdef void _reject_polled_but_not_accepted_offers(self)
    cpdef void reject(self, Offer offer)
    @cython.locals(offer = Offer)
    cpdef Offer _receive_accept(self, object offer_id_final_quantity)
    @cython.locals(offer = Offer)
    cpdef void _receive_reject(self, long offer_id)
    @cython.locals(offer = Offer)
    cpdef void _delete_given_offer(self, long offer_id)
    @cython.locals(available = double)
    cpdef object give(self, object receiver, object good, double quantity, double epsilon=*)
    cpdef void take(self, object receiver, object good, double quantity, double epsilon=*)

cdef int compare_with_ties(double x, double y)
