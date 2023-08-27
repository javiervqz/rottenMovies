from rottenpy import Rotten


if __name__ == "__main__":
  # 
  rot = Rotten(affiliates=["netflix"], genres=["anime"])
  response = rot.tv_series()
  tv_series = response.get("grid").get("list")
  while response["pageInfo"]["hasNextPage"]:
    response = rot.next(response)
    n_tv_series = response.get("grid").get("list")
    tv_series.extend(n_tv_series)

  print(f"{len(tv_series)}--- {tv_series[0].keys()}")