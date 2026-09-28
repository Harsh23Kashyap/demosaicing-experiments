import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline
from nearest_boundary_fixed import dem_nearest_fixed

def test_constant_odd_even():
    for h in (2,3,4,5,7):
        for w in (2,3,4,5,7):
            rgb=np.zeros((h,w,3));rgb[:]=(.2,.5,.8)
            m=pipeline.mosaic_rggb(rgb)
            actual=dem_nearest_fixed(m)
            np.testing.assert_allclose(actual,rgb,atol=0,rtol=0)

def test_observed_cfa_sites_all_parities():
    for h in (3,4,5,6):
        for w in (3,4,5,6):
            m=np.random.default_rng(h*100+w).random((h,w))
            out=dem_nearest_fixed(m)
            assert out.shape==(h,w,3) and np.isfinite(out).all()
            np.testing.assert_array_equal(out[0::2,0::2,0],m[0::2,0::2])
            np.testing.assert_array_equal(out[0::2,1::2,1],m[0::2,1::2])
            np.testing.assert_array_equal(out[1::2,0::2,1],m[1::2,0::2])
            np.testing.assert_array_equal(out[1::2,1::2,2],m[1::2,1::2])

def test_even_historical_equivalence():
    for h,w in ((2,2),(4,6),(8,8),(12,10)):
        m=np.random.default_rng(h*100+w).random((h,w))
        np.testing.assert_array_equal(dem_nearest_fixed(m),pipeline.dem_nearest(m))

if __name__=='__main__':
    test_constant_odd_even();test_observed_cfa_sites_all_parities();test_even_historical_equivalence();print('nearest odd/even fixed tests pass')
