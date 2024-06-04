from unitree_sdk2py.utils.hz_sample import HZSample

if __name__ ==  "__main__":
    hz=HZSample(2)
    hz.Start()
    while True:
        hz.Sample()

