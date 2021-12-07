# https://mpi4py.readthedocs.io/en/stable/tutorial.html
# https://github.com/arthurdouillard/algo_with_mpi/blob/master/lamport_clock.py

from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD


class LamportClock:
  def __init__(self, rank, size):
    self.rank = rank
    self.size = size
    self.clock = 0
    
  def receive(self):
    req = comm.irecv(source=MPI.ANY_SOURCE)
    timestamp = req.wait()
    new_clock = max(self.clock, timestamp)
    self.clock = new_clock + 1
    print("Nó " + str(self.rank) + " atualizou seu clock para " + str(self.clock) + ".")

  def broadcast(self):
    self.clock += 1
    for r in range(self.size):
      if r == self.rank: continue
      req = comm.isend(self.clock, dest=r)
      req.wait()
    #comm.bcast(self.clock, root=self.rank)
    print("Nó " + str(self.rank) + " fez um broadcast com o clock " + str(self.clock) + ".")


if __name__ == '__main__':
  MIN_DELAY = 2
  MAX_DELAY = 10

  clock = LamportClock(
    comm.Get_rank(),
    comm.Get_size()
  )

  print("Nó " + str(clock.rank) + " inicializado.")
  comm.Barrier()
  print("Nó " + str(clock.rank) + " Passou pela barreira.")

  while (True):
    delay = randrange(MIN_DELAY, MAX_DELAY)
    print("Delay do nó " + str(clock.rank) + ": " + str(delay))
    sleep(delay)
    clock.broadcast()
    clock.receive()
