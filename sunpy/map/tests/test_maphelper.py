import pytest
from sunpy.util.metadata import MetaDict
import sunpy.map
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
from sunpy.coordinates import frames


# test setups
@pytest.fixture
def map_data():
    return np.random.rand(10, 10)


@pytest.fixture
def hpc_test_header():
    return SkyCoord(0*u.arcsec, 0*u.arcsec, observer='earth', obstime='2013-10-28 00:00', frame=frames.Helioprojective)


@pytest.fixture
def hgc_test_header():
    return SkyCoord(70*u.deg, -30*u.deg, observer='earth', obstime='2013-10-28 00:00', frame=frames.HeliographicCarrington)


@pytest.fixture
def hgs_test_header():
    return SkyCoord(-50*u.deg, 50*u.deg, observer='earth',  obstime='2013-10-28 00:00', frame=frames.HeliographicStonyhurst)


@pytest.fixture
def hcc_test_header():
    return SkyCoord(-72241*u.km, 361206.1*u.km, 589951.4*u.km, obstime='2013-10-28 00:00', frame=frames.Heliocentric)


@pytest.fixture
def hpc_test_header_notime():
    return SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective)


# tests
def test_metakeywords():
    meta = sunpy.map.meta_keywords()
    assert isinstance(meta, dict)


# def test_get_observer_meta(hpc_test_header):
#     result = sunpy.map.maphelper._get_observer_meta(hpc_test_header.frame)
#     assert isinstance(result, dict)
#     assert result['dsun_obs'] == hpc_test_header.frame.observer.radius.to_value(u.m)
#     assert result['hgln_obs'] == hpc_test_header.frame.observer.lon.to_value(u.deg)
#     assert result['rsun_ref'] == hpc_test_header.frame.rsun.to_value()


# def test_get_instrument_meta():
#     result = sunpy.map.maphelper._get_instrument_meta(instrument = 'test', exposure = 2, telescope = 'test2')
#     assert isinstance(result, dict)
#     assert result['instrume'] == 'test'
#     assert result['exptime'] == 2
#     assert result['telescop'] == 'test2'

#     # try a keyword that is not understood
#     result = sunpy.map.maphelper._get_instrument_meta(nonkeyword = 'test')
#     assert result == {}


def test_make_fits_header(map_data, hpc_test_header, hgc_test_header, hgs_test_header, hcc_test_header, hpc_test_header_notime):

    # Check that different coordinate frames return header MetaDict or not in the case of HCC
    assert isinstance(sunpy.map.make_fitswcs_header(map_data, hpc_test_header), MetaDict)
    assert isinstance(sunpy.map.make_fitswcs_header(map_data, hgc_test_header), MetaDict)
    assert isinstance(sunpy.map.make_fitswcs_header(map_data, hgs_test_header), MetaDict)
    # Raise the HCC error
    with pytest.raises(ValueError):
        sunpy.map.make_fitswcs_header(map_data, hcc_test_header)

    # Check for when coordinate argument isn't given as an `astropy.coordinate.SkyCoord`
    with pytest.raises(ValueError):
        sunpy.map.make_fitswcs_header(map_data, map_data)

    # Check for when an observation time isn't given
    with pytest.raises(ValueError):
        sunpy.map.make_fitswcs_header(map_data, hpc_test_header_notime)

    # Check that correct information is in header MetaDict including observer for HPC
    header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header)
    assert header['crval1'] == 0
    assert header['crpix1'] == 5.5
    assert header['ctype1'] == 'HPLN-TAN'
    assert header['dsun_obs'] == hpc_test_header.frame.observer.radius.to_value(u.m)

    # Check no observer info for HGS and HGC
    header = sunpy.map.make_fitswcs_header(map_data, hgs_test_header)
    assert header.get('dsun_obs') is None
    header = sunpy.map.make_fitswcs_header(map_data, hgc_test_header)
    assert header.get('dsun_obs') is None

    # Check arguments not given as astropy Quantities
    with pytest.raises(TypeError):
        header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, reference_pixel=[0, 0])
        header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, scale=[0, 0])

    # Check arguments of reference_pixel and scale have to be given in astropy units of pix, and arcsec/pix
    with pytest.raises(u.UnitsError):
        header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, reference_pixel=u.Quantity([0, 0]))
        header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, scale=u.Quantity([0, 0]))
        header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, scale=u.Quantity([0, 0]*u.arcsec))

    # Check keyword helper arguments
    header = sunpy.map.make_fitswcs_header(map_data, hpc_test_header, instrument='test name')
    assert header['instrume'] == 'test name'

    # Check returned MetaDict will make a `sunpy.map.Map`
    map_test = sunpy.map.Map(map_data, header)
    assert isinstance(map_test, sunpy.map.mapbase.GenericMap)
