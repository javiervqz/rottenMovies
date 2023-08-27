from rottenpy import Rotten


if __name__ == "__main__":
  rot = Rotten()
  response = rot.movies_in_theaters()
  next_1 = rot.next(response)
  next_2 = rot.next(next_1)
  print(next_2)