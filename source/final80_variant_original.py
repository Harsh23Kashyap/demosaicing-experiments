import sys, json, numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from pipeline import load_rgb8, srgb_to_linear, mosaic_rggb, to_srgb8, luminance, metrics, conv2, H_C
from scipy.signal import firwin
from skimage.color import rgb2lab
from skimage.filters import sobel
from scipy import ndimage

h1 = firwin(9, 0.58, window='hamming'); HL = np.outer(h1,h1); HL/=HL.sum()
def dem_alleysson_final(m):
    H,W = m.shape; y,x = np.mgrid[0:H,0:W]
    L = conv2(m,HL); d = m-L
    c = 0.5*(conv2(d*((-1.0)**x),H_C)+conv2(d*((-1.0)**y),H_C))
    C3 = conv2(d*((-1.0)**(x+y)),H_C)
    R=L+2*c+C3; G=L-C3; B=L-2*c+C3
    R[0::2,0::2]=m[0::2,0::2]; G[0::2,1::2]=m[0::2,1::2]; G[1::2,0::2]=m[1::2,0::2]; B[1::2,1::2]=m[1::2,1::2]
    return np.dstack([R,G,B])

def artifact(ref8, est8):
    Yr, Ye = luminance(ref8), luminance(est8)
    g = np.hypot(sobel(Yr,axis=0), sobel(Yr,axis=1))
    mask = g >= np.percentile(g,80)
    lr, le = rgb2lab(ref8/255.0), rgb2lab(est8/255.0)
    chroma = np.sqrt((lr[...,1]-le[...,1])**2+(lr[...,2]-le[...,2])**2)
    lerr = np.abs(Yr-Ye)
    lm = ndimage.uniform_filter(lerr,5); ls = ndimage.uniform_filter(lerr**2,5)
    return float(chroma[mask].mean() + np.sqrt(np.maximum(ls-lm**2,0))[mask].mean())

