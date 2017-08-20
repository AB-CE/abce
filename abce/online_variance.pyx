cdef class OnlineVariance:
    def __cinit__(self):
        self.clear()

    cpdef clear(self):
        self.n = 0
        self.M2 = 0.0
        self._mean = 0.0

    cpdef update(self, double x):
        cdef double delta
        cdef double delta2
        cdef int i

        self.n += 1

        delta = x - self._mean
        self._mean += delta / self.n
        delta2 = x - self._mean
        self.M2 += delta * delta2

    cpdef double std(self):
        cdef int _
        if self.n < 2:
            return 0.0
        else:
            return (self.M2 / (self.n - 1)) ** 0.5

    cpdef double mean(self):
        cdef int i
        return self._mean

    cpdef double sum(self):
        cdef int i
        return self._mean * self.n
