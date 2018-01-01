import platform
import start_core_engine
import start_logging_test
import start_delete_create
import start_production_consumption
import start_combinable_actions
import start_return


if __name__ == '__main__':
    print("Logging test, 1 core")
    start_logging_test.main(processes=1)
    print('Iteration of logger testing with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Logging test, 4 cores")
        start_logging_test.main(processes=4)
        print('Iteration of logger testing with multiple processes finished')

    print("\nCore engine test, 1 core")
    start_core_engine.main(processes=1, rounds=50)
    print('Iteration with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Core engine test, 4 cores")
        start_core_engine.main(processes=4, rounds=50)
        print('Iteration with multiple processes finished')

    print("\nCreate/delete, 1 core")
    start_delete_create.main(processes=1, rounds=30)
    print('Iteration with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Create/delete, 4 cores")
        start_delete_create.main(processes=4, rounds=20)
        print('Iteration with multiple processes finished')

    print("PYPY and windows: core functions not tested with multi-processes")

    print("\nProduction and consumption test, 1 core")
    start_production_consumption.main(processes=1)
    print('Iteration of production and consumption testing with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Production and consumption test, 4 cores")
        start_production_consumption.main(processes=4)
        print('Iteration of production and consumption testing with multiple processes finished')

    print("\nCombinable actions test, 1 core")
    start_combinable_actions.main(processes=1, rounds=1)
    print('Iteration of combinable actions with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Combinable actions test, 4 cores")
        start_combinable_actions.main(processes=4, rounds=1)
        print('Iteration of combinable actions with multiple processes finished')

    print("\Returning and parameters test, 1 core")
    start_return.main(processes=1, rounds=5)
    print('Iteration of returning and parameters with 1 core finished')

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("Returning and parameters test, 4 cores")
        start_return.main(processes=4, rounds=5)
        print('Iteration of returning and parameters test with multiple processes finished')
