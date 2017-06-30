import start_core_engine
import start_logging_test
import platform


start_core_engine.main(processes=1, rounds=50)
print('Iteration with 1 core finished')
if platform.system() != 'Windows'
    start_core_engine.main(processes=4, rounds=50)
    print('Iteration with multiple processes finished')
start_logging_test.main(processes=1)
print('Iteration of logger testing with 1 core finished')
if platform.system() != 'Windows'
    start_logging_test.main(processes=4)
    print('Iteration of logger testing with multiple processes finished')
