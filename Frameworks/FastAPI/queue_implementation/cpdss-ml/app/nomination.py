import numpy as np
from numpy.linalg import norm as n


# Convert Nomination in BBLS to Weight in MT
def APItoSG(api):
    sg = 141.5 / (131.5 + api)
    return sg


def BBLStoMT(bbls, sg):
    mt = (bbls * 158.987) / (1000 / sg)
    return mt


def padList(arr, pad):
    length = len(arr)
    if length < pad:
        pad_arr = arr + ([0] * (pad - length))
        return pad_arr
    else:
        return arr


def preprocess(nomination, api, ports):
    nomination = padList(nomination, 7)
    api = padList(api, 7)
    new_nomination = [nom for a, nom in
                      sorted(zip(api, nomination), reverse=True)]  # Nomination (bbls) sorted by descending api
    new_api = [a for a, nom in sorted(zip(api, nomination), reverse=True)]  # API sorted by descending api
    # weight = [BBLStoMT(nom, APItoSG(a)) if nom != 0 else 0 for a, nom in
    #           sorted(zip(api, nomination), reverse=True)]  # Weight (MT) sorted by descending api
    total = [sum(new_nomination), ports]
    feature = new_nomination + new_api + total
    return feature


def cosine(A, B):
    res = np.round(1 - np.dot(A / n(A, axis=1)[:, None], (B / n(B, axis=1)[:, None]).T), 10)
    return res


def getTop(score, voyid, rank):
    top_idx = np.flip(np.argsort(score)[-rank:])
    top_values = [score[i] for i in top_idx]
    top_voy = [voyid[i] for i in top_idx]
    return top_voy, top_values
