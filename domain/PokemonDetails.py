import requests
import csv
import queue
from collections import namedtuple
import threading

POKEMON_API_URL = 'https://pokeapi.co/api/v2/pokemon'
Pokemon = namedtuple('Pokemon', ['id', 'name', 'type_1', 'type_2'])


def get_urls(no_of_pokemon: int) -> queue.Queue:
    """
    get_urls of pokemon from https://pokeapi.co/api/v2/pokemon
    """
    url = POKEMON_API_URL
    q = queue.Queue(maxsize=no_of_pokemon)
    while True:
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError("Problem calling Pokemon API")
        data = res.json()
        url = data['next']
        for u in data["results"]:
            try:
                q.put_nowait(u['url'])
            except queue.Full:
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


def save_csv(pokemons: queue.Queue):
    """
    save_csv saves the details of pokemon
    present in provided list to a csv file
    """
    with open("./pokemon.csv", "w",newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id', 'name', 'type_1', 'type_2'])
        while True:
            try:
                op = pokemons.get_nowait()
                writer.writerow(op)
            except queue.Empty:
                break


def worker(urls_queue: queue.Queue, output_queue:queue.Queue):
    while True:
        try:
            url = urls_queue.get_nowait()
            p = get_pokemon(url)
            output_queue.put(p)
        except queue.Empty:
            break


def main():
    urls_queue = get_urls(30)
    output_queue = queue.Queue()
    threads = []

    for tid in range(3):
        thread = threading.Thread(target=worker, args=(urls_queue, output_queue))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    save_csv(output_queue)


if __name__ == '__main__':
    main()