# Fontes utilizadas:
# https://mpi4py.readthedocs.io/en/stable/tutorial.html
# https://github.com/arthurdouillard/algo_with_mpi/blob/master/lamport_clock.py
# https://pt.wikipedia.org/wiki/Rel%C3%B3gios_de_Lamport

from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD
MIN_DELAY = 0
MAX_DELAY = 10

# Classe utilizada para encapsular e realizar as operações dos processos
class LamportClock:
  # Atribuindo informações iniciais da classe
  def __init__(self, rank, size):
    self.rank = rank
    self.size = size
    self.clock = 0

  def receive(self):
    # Espera receber um clock
    timestamp = comm.recv(source=MPI.ANY_SOURCE, tag=42)
    # Se o clock recebido for maior que o atual, atualiza o clock atual
    # caso contrário, mantém o clock
    if timestamp + 1 > self.clock:
      self.clock = timestamp + 1
      print("Nó " + str(self.rank) + " atualizou seu clock para " + str(self.clock))
    else:
      self.clock = self.clock
      print("Nó " + str(self.rank) + " manteve seu clock " + str(self.clock))

  def event(self):
    # Envia seu clock para o processo 0
    self.clock += 1
    print("Nó " + str(self.rank) + " enviou uma mensagem com o clock " + str(self.clock))
    sleep(0.1)
    comm.send(self.clock, dest=0, tag=42)


if __name__ == '__main__':
  # Instancia a classe
  clock = LamportClock(
    comm.Get_rank(),
    comm.Get_size()
  )

  # Sincroniza os processos
  print("Nó " + str(clock.rank) + " inicializado.")
  comm.Barrier()

  while True:
    # Processo 0 ouvi e sincroniza os clocks
    if clock.rank == 0:
      clock.receive()
    else:
      # Demais processos enviam seu clock de tempo em tempo
      delay = randrange(MIN_DELAY, MAX_DELAY)
      print("Delay do nó " + str(clock.rank) + ": " + str(delay))
      sleep(delay)
      clock.event()
