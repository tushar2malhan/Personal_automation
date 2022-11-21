# Convert Nomination in BBLS to Weight in MT
def APItoSG(api):
    sg = 141.5 / (131.5 + api)
    return sg


def BBLStoMT(bbls, sg):
    mt = (bbls * 158.987) / (1000 / sg)
    return mt


def preprocess(vol, api, maxtol, mintol, onhand):
    # vol, api, maxtol, mintol : list of vol, api and tol of individual cargoes

    nomination = [0, 0, 0]  # nomination, max nomination, min nomination (sum of all cargoes)
    weight = [0, 0, 0]  # weight, max weight, min weight (sum of all cargoes)
    for i in range(len(vol)): # Loop through all cargoes
        a= api[i]
        curr_nomination = [vol[i], (1 + maxtol[i]) * vol[i], (1 - mintol[i]) * vol[i]] # Calculate nom, max nom and min nom of current cargo
        nomination = [sum(x) for x in zip(curr_nomination, nomination)]
        curr_weight = [BBLStoMT(nom, APItoSG(a)) for nom in curr_nomination] # Calculate weight, max weight and min weight of current cargo
        weight = [sum(x) for x in zip(curr_weight, weight)]

    total = [onhand + w for w in weight]
    feature = weight + nomination + total + [onhand ,len(vol)]
    return feature
