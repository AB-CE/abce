import platform
import start_core_engine
import start_logging_test
import start_logging_friendly_names_test
import start_delete_create
import start_production_consumption
import start_combinable_actions
import start_return
import start_custom_database
import start_agent_indexing
import start_agent_numerical_indexing
import start_individual_access
import start_service
import start_transform
import start_messaging
import start_messaging_with_envelope


def run_test(name, test):
    print(name + " test, 1 core")
    test.main(processes=1, rounds=10)
    print('Iteration of %s testing with 1 core finished' % name)

    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        print("%s test, 4 cores" % name)
        test.main(processes=2, rounds=10)
        print('Iteration of %s testing with multiple processes finished' % name)
    else:
        print("PYPY and windows: functions not tested with multi-processes")


if __name__ == '__main__':
    run_test("Logging", start_logging_test)
    run_test("Friendly Names Logging", start_logging_friendly_names_test)
    run_test("Core engine", start_core_engine)
    run_test("Returning and parameters", start_return)
    run_test("Create/Delete", start_delete_create)
    run_test("Production and consumption", start_production_consumption)
    run_test("Combinable actions", start_combinable_actions)
    run_test("Custom Database", start_custom_database)
    run_test("individual agent indexing", start_agent_indexing)
    run_test("individual agent indexing numerical", start_agent_numerical_indexing)
    run_test("start_individual_access", start_individual_access)
    run_test("Test service", start_service)
    run_test("Test Transform method", start_transform)
    run_test("Messaging", start_messaging)
    run_test("Messaging with envelope", start_messaging_with_envelope)
