import abce
from ball import Ball
from killer import Killer
from victim import Victim


def main(processes, rounds):
    simulation = abce.Simulation(processes=processes)

    print('build Killer')
    killer = simulation.build_agents(Killer, 'killer', 1, parameters={'rounds': rounds})
    print('build Victim')
    victims = simulation.build_agents(Victim, 'victim', rounds, parameters={'rounds': rounds})
    print('build Victim loudvictim')
    loudvictims = simulation.build_agents(Victim, 'loudvictim', rounds, parameters={'rounds': rounds})
    print('build AddAgent')
    balls = simulation.build_agents(Ball, 'ball', 0)

    for time in range(rounds):
        simulation.advance_round(time)
        assert len(balls.boing()) == time, len(balls.boing())
        deads = killer.kill_silent()
        for dead in deads:
            simulation.delete_agent(*dead)
        deads = killer.kill_loud()
        for dead in deads:
            simulation.delete_agent(*dead)
        killer.send_message()
        victims.am_I_dead()
        loudvictims.am_I_dead()
        simulation.create_agent(Ball, 'ball')

    simulation.finalize()
    del simulation


if __name__ == '__main__':
    main(processes=1, rounds=30)
    print('Iteration with 1 core finished')
    main(processes=4, rounds=20)
    print('Iteration with multiple processes finished')
