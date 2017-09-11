import platform
import start_core_engine
import start_logging_test
import start_delete_create

if __name__ == '__main__':
    print("Logging test, 1 core")
    start_logging_test.main(processes=1)
    print('Iteration of logger testing with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Logging test, 4 cores")
        start_logging_test.main(processes=4)
        print('Iteration of logger testing with multiple processes finished')

    print("Core engine, 1 core")
    start_core_engine.main(processes=1, rounds=50)
    print('Iteration with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Core engine, 4 cores")
        start_core_engine.main(processes=4, rounds=50)
        print('Iteration with multiple processes finished')

    print("Create/delete, 1 core")
    start_delete_create.main(processes=1, rounds=30)
    print('Iteration with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Create/delete, 4 cores")
        start_delete_create.main(processes=4, rounds=20)
        print('Iteration with multiple processes finished')

    print("PYPY and windows: core functions not tested with multi-processes")
