# raid5.py
import math

def split_data(data: bytes, data_shards: int = 3):
    """
    Para RAID5 con 4 nodos: 3 fragmentos de datos + 1 de paridad.
    Devuelve dict { "1": bytes, "2": bytes, "3": bytes, "4": parity_bytes }.
    """
    # longitud de cada fragmento de datos
    total_len = len(data)
    shard_size = math.ceil(total_len / data_shards)

    # crear los 3 fragmentos, padding con ceros si hace falta
    shards = []
    for i in range(data_shards):
        start = i * shard_size
        end = start + shard_size
        frag = data[start:end]
        if len(frag) < shard_size:
            frag += b'\x00' * (shard_size - len(frag))
        shards.append(bytearray(frag))

    # calcular paridad byte a byte
    parity = bytearray(shard_size)
    for i in range(shard_size):
        p = 0
        for s in shards:
            p ^= s[i]
        parity[i] = p

    # mapear a IDs de nodo: 1,2,3→datos; 4→paridad
    return {
        '1': bytes(shards[0]),
        '2': bytes(shards[1]),
        '3': bytes(shards[2]),
        '4': bytes(parity),
    }
