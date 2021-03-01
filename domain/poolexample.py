import requests
import csv
from collections import namedtuple
from typing import List
from multiprocessing import Pool

POKEMON_API_URL = 'https://pokeapi.co/api/v2/pokemon'
Pokemon = namedtuple('Pokemon', ['id', 'name', 'type_1', 'type_2'])


def get_urls(no_of_pokemon: int) -> List[str]:
    """
    get_urls of pokemon from https://pokeapi.co/api/v2/pokemon
    """
    url = POKEMON_API_URL
    q = []
    while True:
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError("Problem calling Pokemon API")
        data = res.json()
        url = data['next']
        for u in data["results"]:
            q.append(u['url'])
            if len(q) == no_of_pokemon:
                return q


def get_pokemon(url: str) -> Pokemon:
    """
    get_pokemon gets the pokemon details
    from the provided url and returns the
    id, name and types of the pokemon as
    a tuple
    """
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError("Problem calling Pokemon API")
    data = res.json()
    return Pokemon(
        id=data['id'],
        name=data['name'],
        type_1=data['types'][0]['type']['name'],
        type_2=data['types'][1]['type']['name'] if len(data['types']) > 1 else ''
    )


def save_csv(pokemons: List[Pokemon]):
    """
    save_csv saves the details of pokemon
    present in provided list to a csv file
    """
    with open("./pokemon.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id', 'name', 'type_1', 'type_2'])
        writer.writerows(pokemons)


def main():
    urls = get_urls(30)
    print(urls)

    with Pool() as pool:
        pokemons = pool.map(get_pokemon, urls)

    print(pokemons)
    save_csv(pokemons)


if __name__ == '__main__':
    main()