import ulab.numpy as np

def sine(size=512, volume=30000):
    return np.array(np.sin(np.linspace(0, 2*np.pi, size, endpoint=False)) * volume, dtype=np.int16)

def square(size=512, volume=30000):
    return np.concatenate((np.ones(size//2, dtype=np.int16) * volume,
                            np.ones(size//2, dtype=np.int16) * -volume))

def triangle(size=512, min_vol=0, max_vol=30000):
    return np.concatenate((np.linspace(min_vol, max_vol, num=size//2, dtype=np.int16),
                            np.linspace(max_vol, min_vol, num=size//2, dtype=np.int16)))

def saw_down(size=512, volume=30000):
    return np.linspace(volume, -volume, num=size, dtype=np.int16)

def saw_up(size=512, volume=30000):
    return np.linspace(-volume, volume, num=size, dtype=np.int16)