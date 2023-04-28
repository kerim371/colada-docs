# Wave Modeling: simple 3D model

This tutorial is identical to [Simple Wave Modeling 2D](../wave_modeling_simple_2d_model/wave_modeling_simple_2d_model.md) but is aimed at 3D modeling.
We suppose that are familiar with the previous tutorials.

## 3D velocity model building

Start model building from initial parameters.

```python
from h5geopy import h5geo
import numpy as np
import scipy as sp
import scipy.ndimage
import colada
import slicer
import os

# to be able to open hdf5 container in HDFVIEW
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

# setting output directories
out_vol_dir = colada.Util().defaultGeoVolumesDir() +'/'
out_seis_dir = colada.Util().defaultSeisDir() +'/'
out_volcnt_name = "model_3D.h5"
out_vol_name = "model_3D"
out_vol_name_smooth = "model_3D_smooth"
out_geomcnt_name = "geom_3D.h5"
out_geom_name = "geom_3D"

SPATIAL_REFERENCE = h5geo.sr.getAuthName() + ":" + h5geo.sr.getAuthCode()
LENGTH_UNITS = "m"
TEMPORAL_UNITS = "ms"
ANGULAR_UNITS = "degree"
DATA_UNITS = "km/s"
ORIENTATION = 0.0

# model params (x,z)
o = (0,0,0)
d = (12.5,12.5,12.5)
n = (300,200,100)
n1 = int(round(n[2]/3)) # first reflector depth
n2 = int(round(2*n[2]/3)) # second reflector depth

# velocities for the layers
v1 = 1.5
v2 = 2
v3 = 2.5

# is used to smooth velocity model
smooth_radius = 20
```

Then create model:

```python
x = np.arange(o[0],o[0]+d[0]*(n[0]-1),d[0])
y = np.arange(o[1],o[1]+d[1]*(n[1]-1),d[1])
z = np.arange(o[2],o[2]+d[2]*(n[2]-1),d[2])

data = np.zeros(n[::-1]) # reverse `n` so the `data.shape = [nz,ny,nx]`
data[:n1,:,:] = v1
data[n1:n2,:,:] = v2
data[n2:,:,:] = v3
data_smooth = sp.ndimage.uniform_filter(data, smooth_radius)

# flip Z axis as h5geo stores volumes in low-to-high direction (origin is lower left corner)
# also make the order layout to Fortran (h5geo works with column oriented arrays)
data = np.asfortranarray(np.flip(data,0), dtype=np.float32)
data_smooth = np.asfortranarray(np.flip(data_smooth,0), dtype=np.float32)
```

Write data:
```python
p = h5geo.H5VolParam()
p.spatialReference = SPATIAL_REFERENCE
p.lengthUnits = LENGTH_UNITS
p.temporalUnits = TEMPORAL_UNITS
p.angularUnits = ANGULAR_UNITS
p.dataUnits = DATA_UNITS
p.domain = h5geo.Domain.TVDSS
p.orientation = ORIENTATION
p.X0 = o[0]
p.Y0 = o[1]
p.Z0 = o[2]-d[2]*(n[2]-1)
p.dX = d[0]
p.dY = d[1]
p.dZ = d[2]
p.nX = n[0]
p.nY = n[1]
p.nZ = n[2]
p.xChunkSize = 64
p.yChunkSize = 64
p.zChunkSize = 64
p.compression_level = 6

volcnt = h5geo.createVolContainerByName(
      out_vol_dir+out_volcnt_name,
      h5geo.CreationType.OPEN_OR_CREATE)
if not volcnt:
  raise RuntimeError(f"Unable to create Volume container: {out_volcnt_name}")

vol = volcnt.createVol(out_vol_name, p, h5geo.CreationType.CREATE_OR_OVERWRITE)
if not vol:
  raise RuntimeError(f"Unable to create Geo Volume: {out_vol_name}")

status = vol.writeData(data.ravel(), 0,0,0,p.nX,p.nY,p.nZ, DATA_UNITS)
if not status:
  raise RuntimeError(f"Unable to write data to Geo Volume: {out_vol_name}")

volsmooth = volcnt.createVol(out_vol_name_smooth, p, h5geo.CreationType.CREATE_OR_OVERWRITE)
if not volsmooth:
  raise RuntimeError(f"Unable to create Geo Volume: {out_vol_name_smooth}")

status = volsmooth.writeData(data_smooth.ravel(), 0,0,0,p.nX,p.nY,p.nZ, DATA_UNITS)
if not status:
  raise RuntimeError(f"Unable to write data to Geo Volume: {out_vol_name_smooth}")

# add geo volume container to treeview
slicer.util.mainWindow().emitH5FileToBeAdded(volcnt.getH5File().getFileName())

# don't forget to close h5geo (hdf5) objects
del vol
del volsmooth
del volcnt
```

:::{warning}

*h5geo* objects hold reference to *h5gt* object wich is *hdf5* wrapper.
It is **extremely important** to close these objects right after you've done working with them (delete variable is one the possible ways).
If file is opened and `HDF5_USE_FILE_LOCKING=TRUE` then this file will be unavailable for other processes.
If `HDF5_USE_FILE_LOCKING=FALSE` then you are risking to break the file if its content is modified from another process.

:::

### Velocity model visualization

Prepared 3D velocity model:

```{image} model_3d.png
:alt: Colada velocity model 3d
:class: bg-primary
:scale: 70%
:align: center
```

## Geometry for 3D model

```python
# timings
nSamp = 800
sampRate = -2.0

# geometry
src_x0 = 1500
src_dx = 100
src_nx = 8
src_y0 = 1000
src_dy = 100
src_ny = 6
src_z = o[2]

rec_x0 = 1000
rec_dx = 50
rec_nx = 21
rec_y0 = 500
rec_dy = 50
rec_ny = 21
rec_z = o[2]
moveRec = True
```

Fill `H5SeisParam` to create new `H5Seis` object and generate PRESTACK geometry:

```python
# h5geo parameters to create new H5Seis object
p = h5geo.H5SeisParam()
p.spatialReference = SPATIAL_REFERENCE
p.lengthUnits = LENGTH_UNITS
p.temporalUnits = TEMPORAL_UNITS
p.angularUnits = ANGULAR_UNITS
p.dataUnits = "psi"
p.domain = h5geo.Domain.TWT
p.dataType = h5geo.SeisDataType.PRESTACK
p.surveyType = h5geo.SurveyType.THREE_D
p.nTrc = 100
p.nSamp = nSamp
p.srd = 0
p.trcChunk = 1000
p.stdChunk = 100

# create Seismic container
geomcnt = h5geo.createSeisContainerByName(
      out_seis_dir + out_geomcnt_name,
      h5geo.CreationType.OPEN_OR_CREATE)
if not geomcnt:
  raise RuntimeError(f"Unable to create Seis container: {out_geomcnt_name}")

# create H5Seis object
geom = geomcnt.createSeis(out_geom_name, p, h5geo.CreationType.CREATE_OR_OVERWRITE)
if not geom:
  raise RuntimeError(f"Unable to create Seis: {out_geom_name}")

# setting sampling rate
geom.setSampRate(sampRate)

# generate geometry
status = geom.generatePRESTKGeometry(
    src_x0, src_dx, src_nx,
    src_y0, src_dy, src_ny,
    src_z,
    rec_x0, rec_dx, rec_nx,
    rec_y0, rec_dy, rec_ny,
    rec_z,
    ORIENTATION,
    moveRec)

if not status:
  raise RuntimeError(f"Unable to generate geometry: {out_geom_name}")

# add geometry container to treeview
slicer.util.mainWindow().emitH5FileToBeAdded(geomcnt.getH5File().getFileName())

# don't forget to close h5geo (hdf5) objects
del geom
del geomcnt
```

The size xy: 3737.5m*2487.5m
Source geometry along x-axis contains 8 sources at positions from 1500 to 2200m with 100m step.
Along y-axis: from 1000 to 1500m wtih 100m step.
Receivers are spread in in 1000m*1000m (i.e. sp+-500m) with 50m step and they are moved along with sources (`moveRec = True`).

### Geometry check

We can load source and receiver positions for each shot.
For example for the first shot we can see this:

```{image} plot_geometry_3d.png
:alt: Colada plot geometry 3D
:class: bg-primary
:scale: 70%
:align: center
```

<span style="color:red">Red</span> marker shows source position for all these receivers.

## Forward Modeling 

In `Wave Modeling` module set all the parameters that were used in [Simple Wave Modeling 2D tutorial](../wave_modeling_simple_2d_model/wave_modeling_simple_2d_model.md). 
It is also necessary to set *Limit modeling domain* to at least 1000m.
This setting defines the region of the model that is used for every shot computation.

```{image} modeled_shot.png
:alt: Colada modeled shot
:class: bg-primary
:scale: 70%
:align: center
```

## Reverse Time Migration (RTM)

Even if we set *Limit modeling domain* to 0m then **30Gb of RAM** is required for RTM.
Actually expanding this area doesn't greately improves the RTM quality.
As in [2D wave modeling tutorial](../wave_modeling_simple_2d_model/wave_modeling_simple_2d_model.md) we have to set model muting to 412.5m and data muting to mute turning waves.

Velocity model overlayed with RTM:

```{image} rtm.png
:alt: Colada rtm
:class: bg-primary
:scale: 70%
:align: center
```

## Least-Squares Reverse Time Migration (LSRTM)
To run LSRTM about **30Gb of RAM** is requires.

Select true velocity model as *Input*.
*Geometry* same generated shots.
Use same mutings that were used in conventional RTM.

```{image} rtm_lsrtm.png
:alt: Colada rtm and lsrtm
:class: bg-primary
:scale: 70%
:align: center
```

Upper pictures show conventional RTM.
Lower - result LSRTM.

## Full Waveform Inversion (FWI)

FWI with *Limit modeling domain* to 0m also requires **30Gb of RAM**.
Don't forget set starting model *model_3D_smooth* as input.
**Important thing** is to turn on *Replace water velocity/density*. 
This will replace velocity (and density if present) at each iteration.

In *FWI Settings* set min/max velocities to 1000 and 3500 respectively.

```{image} fwi.png
:alt: Colada fwi
:class: bg-primary
:scale: 70%
:align: center
```

Upper pictures show starting smoothed model.
Lower - result 10th FWI iteration.