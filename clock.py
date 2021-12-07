# https://mpi4py.readthedocs.io/en/stable/tutorial.html
# https://github.com/arthurdouillard/algo_with_mpi/blob/master/lamport_clock.py

from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD
MIN_DELAY = 0
MAX_DELAY = 10

class LamportClock:
  def __init__(self, rank, size):
    self.rank = rank
    self.size = size
    self.clock = 0
    
  def receive(self):
    timestamp = comm.recv(source=MPI.ANY_SOURCE, tag=42)
    if timestamp + 1 > self.clock:
      self.clock = timestamp + 1
      print("Nó " + str(self.rank) + " atualizou seu clock para " + str(self.clock))
    else:
      self.clock = self.clock
      print("Nó " + str(self.rank) + " manteve seu clock " + str(self.clock))

  def event(self):
    self.clock += 1
    print("Nó " + str(self.rank) + " enviou uma mensagem com o clock " + str(self.clock))
    sleep(0.1)
    comm.send(self.clock, dest=0, tag=42)


if __name__ == '__main__':
  clock = LamportClock(
    comm.Get_rank(),
    comm.Get_size()
  )

  print("Nó " + str(clock.rank) + " inicializado.")
  comm.Barrier()
  
  while True:
    if clock.rank == 0:
      clock.receive()
    else:
      delay = randrange(MIN_DELAY, MAX_DELAY)
      print("Delay do nó " + str(clock.rank) + ": " + str(delay))
      sleep(delay)
      clock.event()
