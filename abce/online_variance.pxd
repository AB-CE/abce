cdef class OnlineVariance:
    cdef long n
    cdef double* _mean
    cdef double* M2
    cdef size_t length

    cpdef clear(self)
    cpdef update(self, list x)
    cpdef variance(self)
    cpdef sum(self)
    cpdef mean(self)
    cpdef clear(self)

