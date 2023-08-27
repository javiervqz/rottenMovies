import requests

HEADERS = {
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-US,en;q=0.9",
    "Referer":"https://www.rottentomatoes.com/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62"
}

class Rotten(object):
    '''
    affiliates:amazon_prime,amc_plus,apple_tv_plus,apple_tv_us,disney_plus,hulu,max_us,netflix,paramount_plus,peacock,showtime,vudu
    genres:action,adventure,animation,anime,biography,comedy,crime,documentary,drama,entertainment,faith_and_spirituality,fantasy,game_show,health_and_wellness,history,holiday,horror,house_and_garden,kids_and_family,lgbtq,music,musical,mystery_and_thriller,nature,news,reality,romance,sci_fi,short,soap,special_interest,sports,stand_up,talk_show,travel,variety,war,western
    ratings:tv14,tvg,tvma,tvpg,tvy,tvy7
    '''
    def __init__(
            self,
            affiliates = None,
            genres = None,
            ratings = None
    ):
        self.base_url = 'https://www.rottentomatoes.com/napi/browse/'
        self.affiliates = affiliates
        self.genres = genres
        self.ratings = ratings
        
        self._build_session()

    def _process_url(self,endpoint=None, next=None):
        filters_p = []
        if self.affiliates is not None and endpoint != 'movies_in_theaters':
            affiliates = ','.join(self.affiliates)
            affiliates_p = f"affiliates:{affiliates}"
            filters_p.append(affiliates_p)
        if self.genres is not None:
            genres = ','.join(self.genres)
            genres_p = f"genres:{genres}"
            filters_p.append(genres_p)
        if self.ratings is not None:
            ratings = ','.join(self.ratings)
            ratings_p = f"ratings:{ratings}"
            filters_p.append(ratings_p)
        
        filters = '~'.join(filters_p)
        # print(filters)

        endpoint_p = "_".join(endpoint.split("_")[:3])
        # print(endpoint_p)

        if next is None and len(filters_p) > 0:
            return f"{self.base_url}{endpoint_p}/{filters}?page=1"
        elif len(filters_p)>0:
            return f"{self.base_url}{endpoint_p}/{filters}?after={next}"
        else:
            return f"{self.base_url}{endpoint_p}"

        # if next is None:
        #     url = f"{self.base_url}{endpoint}/{affiliates_p}?page=1"
        #     return url

    def _build_session(self):
        self._session = requests.Session()

    def _get(self, url):
        with self._session as s:
          response = s.request("GET", url)
          response.raise_for_status()
          result = response.json()

        return result
    
    def next(self, result):
        page_info = result.get("pageInfo")
        endpoint = result.get("grid").get("id")  

        end_cursor = page_info.get("endCursor")
        next_url = self._process_url(endpoint=endpoint, next=end_cursor)
        return self._get(next_url)      

        # if page_info.get("hasNextPage"):
        #     # end_cursor = page_info.get("endCursor")
        #     # next_url = self._process_url(endpoint=endpoint, next=end_cursor)
        #     # return self._get(next_url)
        # else:
        #     print("End reached")
        #     return None
        
    def movies_in_theaters(self):
        url = self._process_url(endpoint="movies_in_theaters")
        # print(url)
        return self._get(url)
    
    def movies_at_home(self):
        # url = f"{self.base_url}movies_at_home/"
        url = self._process_url(endpoint="movies_at_home")
        print(url)
        return self._get(url)
    
    def tv_series(self):
      url = self._process_url(endpoint="tv_series_browse")
      return self._get(url)
        
        
        

        
# /sort:popular?after=Mjc%3D
# genres:action~ratings:pg
# /affiliates:netflix~sort:popular?page=1
# /affiliates:max_us,netflix~sort:popular?page=1
# /affiliates:max_us,netflix~sort:popular?after=Mjk=