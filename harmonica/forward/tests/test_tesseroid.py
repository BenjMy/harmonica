"""
Test forward modellig for point masses.
"""
import numpy as np
import numpy.testing as npt
from pytest import raises

from ..tesseroid import (
    _distance_tesseroid_point,
    _tesseroid_dimensions,
    adaptive_discretization,
)


def test_distance_tesseroid_point():
    "Test distance between tesseroid and computation point"
    longitude_p, latitude_p, radius_p = 0.0, 0.0, 1.0
    d_lon, d_lat, d_radius = 2.0, 2.0, 1.0
    tesseroid = [
        longitude_p - d_lon / 2,
        longitude_p + d_lon / 2,
        latitude_p - d_lat / 2,
        latitude_p + d_lat / 2,
        radius_p - d_radius / 2,
        radius_p + d_radius / 2,
    ]
    # Computation point on the center of the tesseroid
    point = [longitude_p, latitude_p, radius_p]
    npt.assert_allclose(_distance_tesseroid_point(point, tesseroid), 0.0)
    # Computation point and tesseroid center with same longitude and latitude
    radius = radius_p + 1.0
    point = [longitude_p, latitude_p, radius]
    npt.assert_allclose(_distance_tesseroid_point(point, tesseroid), 1.0)
    # Computation point and tesseroid center on equator and same radius
    longitude = 3.0
    point = [longitude, latitude_p, radius_p]
    distance = 2 * radius_p * np.sin(0.5 * np.radians(abs(longitude - longitude_p)))
    npt.assert_allclose(_distance_tesseroid_point(point, tesseroid), distance)
    # Computation point and tesseroid center on same meridian and radius
    latitude = 3.0
    point = [longitude_p, latitude, radius_p]
    distance = 2 * radius_p * np.sin(0.5 * np.radians(abs(latitude - latitude_p)))
    npt.assert_allclose(_distance_tesseroid_point(point, tesseroid), distance)


def test_tesseroid_dimensions():
    "Test calculation of tesseroid dimensions"
    # Tesseroid on equator
    w, e, s, n, bottom, top = -1.0, 1.0, -1.0, 1.0, 0.5, 1.5
    tesseroid = [w, e, s, n, bottom, top]
    L_lon, L_lat = top * np.radians(abs(e - w)), top * np.radians(abs(n - s))
    L_r = top - bottom
    npt.assert_allclose((L_lon, L_lat, L_r), _tesseroid_dimensions(tesseroid))


def test_adaptive_discretization():
    "Test if closer computation points increase the tesseroid discretization"
    for radial_discretization in [True, False]:
        tesseroid = [-10.0, 10.0, -10.0, 10.0, 0.5, 1.0]
        radii = [1.5, 2.0, 3.0, 5.0, 10.0]
        # Only if 2D adaptive discretization set point on the surface of the tesseroid
        if radial_discretization:
            radii.insert(0, 1.01)
        else:
            radii.insert(0, 1.0)
        number_of_splits = []
        for radius in radii:
            coordinates = [0.0, 0.0, radius]
            smaller_tesseroids = adaptive_discretization(
                coordinates,
                tesseroid,
                distance_size_ratio=10.0,
                radial_discretization=radial_discretization,
            )
            number_of_splits.append(smaller_tesseroids.shape[0])
        for i in range(1, len(number_of_splits)):
            assert number_of_splits[i - 1] >= number_of_splits[i]
