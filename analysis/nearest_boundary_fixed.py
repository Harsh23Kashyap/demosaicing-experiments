"""Corrected nearest-neighbour floor for odd dimensions; historic source stays frozen.

Choose only in-bounds CFA sites of each RGGB colour. This is not substituted
into historical CSV replay or timings, all of whose source images have even sizes.
"""
import numpy as np

def dem_nearest_fixed(m):
    h,w=m.shape
    if h<2 or w<2:
        raise ValueError('RGGB nearest-neighbour floor requires both dimensions >= 2')
    y,x=np.indices((h,w))
    r_y=np.minimum(y//2*2,h-1-(h-1)%2)
    r_x=np.minimum(x//2*2,w-1-(w-1)%2)
    b_y=np.minimum(y//2*2+1,h-1 if h%2==0 else h-2)
    b_x=np.minimum(x//2*2+1,w-1 if w%2==0 else w-2)
    # On green rows, retain the measured green; on red/blue sites, choose
    # the adjacent green site within the same row, preferring right unless
    # it falls off an odd-width edge.
    g_x=np.where((y%2==0)&(x%2==0),np.where(x+1<w,x+1,x-1),
                 np.where((y%2==1)&(x%2==1),x-1,x))
    return np.stack([m[r_y,r_x],m[y,g_x],m[b_y,b_x]],axis=-1)
