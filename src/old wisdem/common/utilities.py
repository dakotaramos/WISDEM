#!/usr/bin/env python
# encoding: utf-8
"""
utilities.py

Created by Andrew Ning on 2013-05-31.
Copyright (c) NREL. All rights reserved.
"""

import os
import shutil
import numpy as np
import atexit
from math import pi
from scipy import integrate
from csystem import DirectionVector

RPM2RS = pi/30.0
RS2RPM = 30.0/pi


def exe_path(defaultPath, exeName, searchPath):
    """find path to an executable

    Parameters
    ----------
    defaultPath : str
        path where executable should be located by default (may be None if no default exists)
    exeName : str
        name of the executable without extension (not case sensitive)
    searchPath : str
        path to look for executable in

    Returns
    -------
    exe_path : str
        full path to the executable

    """

    found = False

    if defaultPath is not None and os.path.exists(defaultPath):
        foundPath = defaultPath
        found = True

    else:
        names = [exeName]  # seems to be case-insensitive
        extensions = ['', '.exe']
        for filename in [(os.path.join(searchPath, name + ext)) for name in names for ext in extensions]:
            if os.path.exists(filename):
                foundPath = filename
                found = True
                break

    if not found:
        raise Exception('Did not find ' + exeName + ' executable')

    return foundPath



def mktmpdir(dirname, DEBUG, tmp_files=None):
    """create a working directory at location dirname"""

    # create working directory
    try:
        os.mkdir(dirname)

    except OSError as e:
        if e.errno != 17:  # silently ignore case where directory exists
            print 'OS error({0}): {1}'.format(e.errno, e.strerror)

    # schedule deletion of working directory
    @atexit.register
    def cleanup():
        if not DEBUG:
            shutil.rmtree(dirname)

            if tmp_files is not None:
                for f in tmp_files:
                    os.remove(f)



# def rmdir(dirname):
#     """remove working directory dirname"""

#     shutil.rmtree(dirname)


def cosd(value):
    """cosine of value where value is given in degrees"""

    return np.cos(np.radians(value))


def sind(value):
    """sine of value where value is given in degrees"""

    return np.sin(np.radians(value))


def tand(value):
    """tangent of value where value is given in degrees"""

    return np.tan(np.radians(value))


# def curvedblade(r, precone, precurve):

#     # blade geometry in azimuthal coordinate
#     azm = DirectionVector(0, 0, r).bladeToAzimuth(precone)

#     x_azim = azm.x + precurve  # precurve defined here as an offset in +x azimuthal direction (thus preserving rotor radius)
#     y_azim = np.zeros_like(r)
#     z_azim = azm.z


#     # compute total coning angle for purposes of relative velocity
#     cone_angle = np.zeros_like(r)
#     cone_angle[0] = np.arctan2(-(x_azim[1] - x_azim[0]), z_azim[1] - z_azim[0])
#     cone_angle[1:-1] = 0.5*(np.arctan2(-(x_azim[2:] - x_azim[1:-1]), z_azim[2:] - z_azim[1:-1])
#                             + np.arctan2(-(x_azim[1:-1] - x_azim[:-2]), z_azim[1:-1] - z_azim[:-2]))
#     cone_angle[-1] = np.arctan2(-(x_azim[-1] - x_azim[-2]), z_azim[-1] - z_azim[-2])


#     # compute path length of blade
#     ds = np.sqrt((x_azim[1:] - x_azim[:-1])**2 + (z_azim[1:] - z_azim[:-1])**2)
#     s = r[0] + np.concatenate([[0.0], np.cumsum(ds)])

#     return x_azim, y_azim, z_azim, cone_angle, s


# def curvedblade(r, precone, precurve):

#     # blade geometry in azimuthal coordinate
#     azm = DirectionVector(precurve, 0*r, r).bladeToAzimuth(precone)

#     rotorR = azm.z[-1]

#     # compute total coning angle for purposes of relative velocity
#     cone_angle = np.zeros_like(r)
#     cone_angle[0] = np.arctan2(-(azm.x[1] - azm.x[0]), azm.z[1] - azm.z[0])
#     cone_angle[1:-1] = 0.5*(np.arctan2(-(azm.x[2:] - azm.x[1:-1]), azm.z[2:] - azm.z[1:-1])
#                             + np.arctan2(-(azm.x[1:-1] - azm.x[:-2]), azm.z[1:-1] - azm.z[:-2]))
#     cone_angle[-1] = np.arctan2(-(azm.x[-1] - azm.x[-2]), azm.z[-1] - azm.z[-2])

#     # compute path length of blade
#     ds = np.sqrt((azm.x[1:] - azm.x[:-1])**2 + (azm.z[1:] - azm.z[:-1])**2)
#     s = r[0] + np.concatenate([[0.0], np.cumsum(ds)])

#     return azm, rotorR, cone_angle, s



def bladePositionAzimuthCS(r, precone):
    """compute coordiantes of blade in azimuthal coordinate system
    accounting for precone and precurve

    """
    Rhub = r[0]

    # z-direction
    integrandZ = 1.0/np.sqrt(1 + tand(precone)**2)
    z_azim = Rhub + np.concatenate(([0.0], integrate.cumtrapz(integrandZ, r)))


    # x-direction
    integrandX = np.zeros_like(integrandZ)
    idx = (precone != 0)  # avoid divide by zero
    integrandX[idx] = 1.0/np.sqrt(1 + 1.0/tand(precone[idx])**2)
    x_azim = np.concatenate(([0.0], integrate.cumtrapz(integrandX, r)))

    if precone[0] > 0:
        x_azim *= -1

    return DirectionVector(x_azim, 0*x_azim, z_azim)


def actualDiameter(r, precone):

    return 2.0 * bladePositionAzimuthCS(r, precone).z[-1]