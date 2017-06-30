import start_core_engine
import start_logging_test


start_core_engine.main(processes=1, rounds=5)
print('Iteration with 1 core finished')
start_core_engine.main(processes=4, rounds=5)
print('Iteration with multiple processes finished')
start_logging_test.main(processes=1)
start_logging_test.main(processes=4)
