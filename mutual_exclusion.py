# Fontes Utilizadas
# https://pt.wikipedia.org/wiki/Rel%C3%B3gios_de_Lamport

from random import randrange
from random import randint
from time import sleep
from mpi4py import MPI

MIN_DELAY = 5
MAX_DELAY = 25
comm = MPI.COMM_WORLD

# Classe utilizada para encapsular e realizar as operações dos processos
class LamportClock:
  # Atribuindo informações iniciais da classe
  def __init__(self, rank, size):
    self.rank = rank
    self.size = size
    self.clock = 0
    self.queue = []

  def receive(self):
    # Espera receber uma solicitação em forma de uma tupla (rank, clock)
    queue = comm.recv(source=MPI.ANY_SOURCE, tag=42)
    # Adiciona a solicitação na fila
    self.queue.append(queue)
    print("Nó " + str(self.rank) + " recebeu uma mensagem do nó " + str(queue[0]) + " com clock " + str(queue[1]))

  def event(self):
    # Completou um ciclo e deseja entrar na região critica
    self.clock += 1
    print("Nó " + str(self.rank) + " enviou uma mensagem com o clock " + str(self.clock))
    sleep(0.1)
    # Envia uma solicitação ao processo 0, fornecendo seu rank e clock
    comm.send((self.rank, self.clock), dest=0, tag=42)

if __name__ == '__main__':
  # Instancia a classe
  clock = LamportClock(
    comm.Get_rank(),
    comm.Get_size()
  )

  # Sincroniza os processos
  print("Nó " + str(clock.rank) + " inicializado.")
  comm.Barrier()

  # Se for o processo 0
  if clock.rank == 0:
    while True:
      # Espera receber 3 requisições
      while len(clock.queue) < 3:
        print("Nó " + str(clock.rank) + " está esperando 3 mensagens... Fila: " + str(clock.queue))
        clock.receive()
      # Escolhe a com menor timestamp
      # ou seja,
      # Escolhe o processo que realizou menos ciclos
      # Em caso de empate, a solicitação será escolhida pela ordem na lista
      # Primeiro a chegar, primeiro a sair
      msg_to_send = clock.queue[0]
      for i in range(1, len(clock.queue)):
        timestamp = clock.queue[i][1]
        if timestamp < msg_to_send[1]:
          msg_to_send = clock.queue[i]
      # Concede a solicitação escolhida, acesso a região crítica
      print("[!] Nó " + str(msg_to_send[0]) + " está na região crítica.")
      delay = randint(10, 50)
      counter = 0
      # Enquanto um processo está na região critica,
      # o processo 0 continua recebendo requisições
      while True:
        while not comm.iprobe(source=MPI.ANY_SOURCE, tag=42):
          sleep(0.1)
          counter += 1
          if counter % 5 == 0:
            print(str(round(counter/delay * 100)) + "%")
          if counter >= delay:
            break
        if counter < delay:
          # Recebeu uma requisição enquanto está na região crítica
          clock.receive()
        else:
          break
      # Quando um processo saí da região critica, sua solicitação é removida da fila
      clock.queue.remove(msg_to_send)
      print("[!] Nó " + str(msg_to_send[0]) + " saiu da região crítica.")
  # Para os demais processos
  else:
    while True:
      # Escolhem um valor entre MIN_DELAY e MAX_DELAY
      delay = randrange(MIN_DELAY, MAX_DELAY)
      # Dormem durante esse tempo
      sleep(delay)
      # Inicia um novo evento
      clock.event()
