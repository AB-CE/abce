import abcEconomics
from ball import Ball
from killer import Killer
from victim import Victim


def main(processes, rounds):
    simulation = abcEconomics.Simulation(processes=processes)

    print('build Killer')
    killer = simulation.build_agents(Killer, 'killer', 1)
    print('build Victim')
    victims = simulation.build_agents(Victim, 'victim', rounds)
    print('build Victim loudvictim')
    loudvictims = simulation.build_agents(Victim, 'loudvictim', rounds)
    print('build AddAgent')
    balls = simulation.build_agents(Ball, 'ball', 0)

    for time in range(rounds):
        simulation.advance_round(time)
        assert len(balls) == time, len(balls)
        deads = killer.kill_silent()
        victims.delete_agents(deads)
        deads = killer.kill_loud()
        loudvictims.delete_agents(deads)
        victims.am_I_dead()
        loudvictims.am_I_dead()
        balls.create_agents(Ball, 1)

    simulation.finalize()
    del simulation


if __name__ == '__main__':
    main(processes=1, rounds=30)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=20)
    print('Iteration with multiple processes finished')
