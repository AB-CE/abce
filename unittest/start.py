import platform
import start_core_engine
import start_logging_test

if __name__ == '__main__':
    start_logging_test.main(processes=1)
    print('Iteration of logger testing with 1 core finished')
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        start_logging_test.main(processes=4)
        print('Iteration of logger testing with multiple processes finished')
    start_core_engine.main(processes=1, rounds=50)
    print('Iteration with 1 core finished')
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        start_core_engine.main(processes=4, rounds=50)
        print('Iteration with multiple processes finished')
