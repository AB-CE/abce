cdef class OnlineVariance:
    cdef long n
    cdef double _mean
    cdef double M2

    cpdef clear(self)
    cpdef update(self, double x)
    cpdef double std(self)
    cpdef double sum(self)
    cpdef double mean(self)
    cpdef clear(self)

