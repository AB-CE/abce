import platform
import start_core_engine
import start_logging_test
import start_delete_create
import start_production_consumption
import start_combinable_actions
import start_return
import start_buy
import start_sell
import start_buy_shipping
import start_sell_shipping


def run_test(name, test):
    print(name + " test, 1 core")
    test.main(processes=1)
    print('Iteration of %s testing with 1 core finished' % name)

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("%s test, 4 cores" % name)
        test.main(processes=4)
        print('Iteration of %s testing with multiple processes finished' % name)
    else:
        print("PYPY and windows: functions not tested with multi-processes")


if __name__ == '__main__':
    run_test("Logging", start_logging_test)
    run_test("Core engine", start_core_engine)
    run_test("buying", start_buy)
    run_test("selling with shipping delay", start_sell)
    run_test("buying shipping delay ", start_buy_shipping)
    run_test("selling", start_sell_shipping)
    run_test("Create/Delete", start_delete_create)
    run_test("Production and consumption", start_production_consumption)
    run_test("Combinable actions", start_combinable_actions)
    run_test("Returning and parameters", start_return)
