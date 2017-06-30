from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
import cython

cdef class OnlineVariance:


    def __cinit__(self, size_t length):
        self.M2 = <double*> PyMem_Malloc(length * sizeof(double))
        self._mean = <double*> PyMem_Malloc(length * sizeof(double))
        self.length = length
        self.clear()

    cpdef clear(self):
        cdef int i
        for i in range(self.length):
            self.n = 0
            self.M2[i] = 0.0
            self._mean[i] = 0.0

    cpdef update(self, list x):
        cdef double* delta = <double*> PyMem_Malloc(self.length * sizeof(double))
        cdef double* delta2 = <double*> PyMem_Malloc(self.length * sizeof(double))
        cdef int i

        self.n += 1

        for i in range(self.length):
            delta[i] = x[i] - self._mean[i]
            self._mean[i] += delta[i] / self.n
            delta2[i] = x[i] - self._mean[i]
            self.M2[i] += delta[i] * delta2[i]

        PyMem_Free(delta)
        PyMem_Free(delta2)

    cpdef std(self):
        cdef int _
        if self.n < 2:
            return [0.0 for _ in range(self.length)]
        else:
            return [(self.M2[i] / (self.n - 1)) ** 0.5  for i in range(self.length)]

    cpdef mean(self):
        cdef int i
        return [self._mean[i] for i in range(self.length)]

    cpdef sum(self):
        cdef int i
        return [self._mean[i] * self.n for i in range(self.length)]


    def __dealloc__(self):
        PyMem_Free(self.M2)
        PyMem_Free(self._mean)


