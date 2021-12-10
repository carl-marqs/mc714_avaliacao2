# https://en.wikipedia.org/wiki/Leader_election

from random import randint
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD

if __name__ == '__main__':
  # obter informações da rede
  rank = comm.Get_rank()
  size = comm.Get_size()
  # escolher prioridade aleatoriamete
  priority = randint(0, 1000)
  # obter vizinhos
  if rank == 0:
    left_neighbor = size - 1
    right_neighbor = rank + 1
  elif rank == size - 1:
    left_neighbor = size - 2
    right_neighbor = 0
  else:
    left_neighbor = (rank - 1) % size
    right_neighbor = (rank + 1) % size
  # inicializar líder desconhecido
  leader_rank = -1
  leader_priority = -1
  # sincronizar
  print(str(rank) + ": inicializado com prioridade " + str(priority) + ".")
  comm.Barrier()

  if rank == 0:
    # envia ele próprio como melhor candidato para o vizinho direito
    print(str(rank) + ": eu sou o melhor candidato, pois tenho prioridade " + str(priority))
    sleep(0.1)
    comm.send((rank, priority), dest=right_neighbor, tag=42)
    # espera receber o resultado do vizinho esquerdo
    (leader_rank, leader_priority) = comm.recv(source=left_neighbor, tag=42)
    # repassar o resultado da eleição para o vizinho direito
    comm.send((leader_rank, leader_priority), dest=right_neighbor, tag=42)
  else:
    # esperar receber, do vizinho da esquerda, o melhor candidato até então
    (best_rank, best_priority) = comm.recv(source=left_neighbor, tag=42)
    # verificar se eu sou o lider
    if best_priority < priority:
      best_rank = rank
      best_priority = priority
      print(str(rank) + ": não, EU sou o melhor candidato, pois tenho prioridade " + str(priority))
    else:
      print(str(rank) + ": realmente, o nó " + str(best_rank) + " é o melhor candidato.")
    # enviar candidato ao vizinho da direita
    sleep(0.1)
    comm.send((best_rank, best_priority), dest=right_neighbor, tag=42)
    # esperar resultado do vizinho da esquerda
    (leader_rank, leader_priority) = comm.recv(source=left_neighbor, tag=42)
    # Repassar líder
    if rank != size - 1:
      comm.send((leader_rank, best_priority), dest=right_neighbor, tag=42)
  # exibir resultado da eleição
  if leader_rank != rank:
    print(str(rank) + ": ok, o líder é o nó " + str(leader_rank) + "...")
  else:
    print(str(rank) + ": viu? eu disse, o líder sou eu!")
