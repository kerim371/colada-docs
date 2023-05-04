# Wave Modeling: simple 2D model

Before starting to work with wave modeling/migration/inversion we must have at least two things:
1) velocity model
2) geometry

Velocity model is a Geo Volume object.
It may be read from SEGY or be prepared using Python/Julia interface.

Geometry is either *H5Seis* object or SEGY files.
It includes at least Source/Receiver positions (XYZ coordinates).
Geometry may be generated using *Seismic* module under *Geometry* section.
It is pretty straightforward.

In this tutorial we will use Python interface to build model and generate geometry.

## 2D velocity model building

Let's start from setting initial data to build model with two horizontal layers:

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
out_volcnt_name = "model_2D.h5"
out_vol_name = "model_2D"
out_vol_name_smooth = "model_2D_smooth"
out_geomcnt_name = "geom_2D.h5"
out_geom_name = "geom_2D"

SPATIAL_REFERENCE = h5geo.sr.getAuthName() + ":" + h5geo.sr.getAuthCode()
LENGTH_UNITS = "m"
TEMPORAL_UNITS = "ms"
ANGULAR_UNITS = "degree"
DATA_UNITS = "km/s"
ORIENTATION = 0.0

# model params (x,z)
o = (0,0)
d = (12.5,12.5)
n = (300,100)
n1 = int(round(n[1]/3)) # first reflector depth
n2 = int(round(2*n[1]/3)) # second reflector depth

# velocities for the layers
v1 = 1.5
v2 = 2
v3 = 2.5

# is used to smooth velocity model
smooth_radius = 20
```
Most of this should be pretty understandable
The most important here is model parameters like size `n` of the model, origin `o`, spacings `d`.
`v1,v2,v3` define first, second and third layer velocities respectively.
`smooth_radius` defines the number of points per axis to apply filter to the model to get smoothed velocity model.

Second step is to create velocity model represented by `numpy` array. 
In our case the model is very simple:

```python
x = np.arange(o[0],o[0]+d[0]*(n[0]-1),d[0])
z = np.arange(o[1],o[1]+d[1]*(n[1]-1),d[1])

data = np.zeros(n[::-1]) # reverse `n` so the `data.shape = [nz,nx]`
data[:n1,:] = v1
data[n1:n2,:] = v2
data[n2:,:] = v3
data_smooth = sp.ndimage.uniform_filter(data, smooth_radius)

# flip Z axis as h5geo stores volumes in low-to-high direction (origin is lower left corner)
# also make the order layout to Fortran (h5geo works with column oriented arrays)
data = np.asfortranarray(np.flip(data,0), dtype=np.float32)
data_smooth = np.asfortranarray(np.flip(data_smooth,0), dtype=np.float32)
```

The most important here is to understand which direction correspond to wich axis.
If we work with 2D model then numpy array should be of shape `[nz,nx]`.
`data` is our model (`numpy` array).
`data_smooth` is smoothed model.
Here is the trick: Colada uses origin as lower left corner of the model. Thus we need to flip `z` axis.

Also it worth to notice that `h5geo` works only with `1D` and `2D` Fortran memory ordered arrays and the writable data usually stored as `float32`.

:::{note}

Pay attension that we will alway use Fortran memory layout when working with `h5geo`. 
And don't forget to cast data to 1D or 2D array of `float32`.

:::

The last step is to create `H5Seis` object within seismic container and write the generated model:
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
p.Y0 = 0.0
p.Z0 = o[1]-d[1]*(n[1]-1)
p.dX = d[0]
p.dY = 1.0
p.dZ = d[1]
p.nX = n[0]
p.nY = 1
p.nZ = n[1]
p.xChunkSize = 64
p.yChunkSize = 1
p.zChunkSize = 64
p.compression_level = 6

# create Geo Volume container
volcnt = h5geo.createVolContainerByName(
      out_vol_dir+out_volcnt_name,
      h5geo.CreationType.OPEN_OR_CREATE)
if not volcnt:
  raise RuntimeError(f"Unable to create Volume container: {out_volcnt_name}")

# create Geo Volume object (H5Vol)
vol = volcnt.createVol(out_vol_name, p, h5geo.CreationType.CREATE_OR_OVERWRITE)
if not vol:
  raise RuntimeError(f"Unable to create Geo Volume: {out_vol_name}")

# write the data to Geo Volume
status = vol.writeData(data.ravel(), 0,0,0,p.nX,p.nY,p.nZ, DATA_UNITS)
if not status:
  raise RuntimeError(f"Unable to write data to Geo Volume: {out_vol_name}")

# create Geo Volume for smotthed model
volsmooth = volcnt.createVol(out_vol_name_smooth, p, h5geo.CreationType.CREATE_OR_OVERWRITE)
if not volsmooth:
  raise RuntimeError(f"Unable to create Geo Volume: {out_vol_name_smooth}")

# write smoothed data to Geo Volume
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
It is **extremely important** to close these objects right after you've done working with them (delete variable is one of the possible ways).
If file is opened and `HDF5_USE_FILE_LOCKING=TRUE` then this file will be unavailable for other processes.
If `HDF5_USE_FILE_LOCKING=FALSE` then you are risking to break the file if its content is modified from another process.

:::

The variable `p` is used to create new `H5Vol` object.
Almost all its fields are self descridable.

`X0,Y0,Z0` define origin (in legth units).
`dX,dY,dZ` are spacings aling `X,Y,Z` axes respectively.
`nX,nY,nZ` are dimensions.
`orientation` is orientation around `Z` axis.

Chunking is important for IO perfomance. 
In this case we are trying to imitate `ZGY` format using chunking equal to 64.
`compression_level` is used to compress the data.

:::{note}

Geo Volume must not contain zeroed or negative spacings (i.e. it must have `dX,dY,dZ > 0`).
Also `nX,nY,nZ` must be `> 0`.

:::

### Velocity model visualization

Generated model should be visible in Geo Volume treeview.

Load Geo Volume. 
The picture should be similar to this one:

```{image} model_2d.png
:alt: Colada velocity model 2d
:class: bg-primary
:scale: 70%
:align: center
```

## Geometry for 2D model

There is no need to write the algorithm for calculating geometry.
It is already done in `h5geo`.

So we start by setting the initial data for geometry:
```python
# timings
nSamp = 800
sampRate = -2.0

# geometry
src_x0 = 1500
src_dx = 100
src_nx = 8
src_y0 = 0
src_dy = 0
src_ny = 1
src_z = o[1]

rec_x0 = 0
rec_dx = 50
rec_nx = 61
rec_y0 = 0
rec_dy = 0
rec_ny = 1
rec_z = o[1]
moveRec = True
```

Then we simpy fill `H5SeisParam` fields to create new `H5Seis` object within seismic container and call the function `generatePRESTKGeometry` to generate PRESTACK geometry:

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
p.trcChunk = 100
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

The model has length 3737.5m.
Source geometry contains 8 sources at positions from 1500 to 2200m with 100m step.
Receivers are moved along with sources (`moveRec = True`), that means for the first source receivers are spread from 0m to 3000m with 50m step. 
For the second source receivers are spread from 100m to 3100m and so on. 

### Geometry check

Geometry container should be added to the Seismic treeview. 

First thing to do is to add sorting.
As we have PRESTACK geometry then we can add `SRCX` sorting.
For that go to the `Seismic` module, set active seismic at the top (one may use drag&drop from treeview), open *Sorting* section and double click on `SRCX` header.
This will cause `SRCX` to appear in the right list.
Then click `Add Sorting`.

After that `SRCX` sorted data may be loaded either as any type of mesh or loaded to table.
We will load it to table and plot.

Open *Load to Table* section, click on combobox *Select a Table->Create new Table*.
Most widgets become enabled. In the `Sorted trace headers` section set `SRCX` as *primary key* (PKey). Then click on *plus* button to add secondary key (SKey) and set it to `GRPX` and click *Load sorted trace headers*.

Change layout by clicking the button on the toolbar similar to this ![](LayoutFull.png) and choose one containing *plot*. 

Go to the *Plots* module click `Create new PlotChart`.
This simply creates new plot.
To add data to it click `Create new PlotSeries`.
Then click on `Series` tab. Set the parameters:
* Plot type *Scatter*
* Input table: *Table*
* X Axis column: *GRPX*
* Y Axis column: *SRCX*
* Marker style: *square*
* Line style: *None*

After some manipulations one can achieve something like that:

```{image} plot_geometry_2d.png
:alt: Colada plot geometry 2D
:class: bg-primary
:scale: 70%
:align: center
```

:::{note}

Loaded trace headers are also available in *Tables* module.
But be aware that tables with n*1000 rows work slow and may greatly reduce the perfomance.

:::

## Forward Modeling

Go to the `Wave Modeling` module.

Physical Parameters:
* Velocity: previously generated `model_2D.h5`

Field Records (Geometry):
* File format: H5SEIS
* Geometry: previously generated `geom_2D.h5`
* PKey (Primary Key): SP
* Source x: SRCX
* Receiver x: GRPX

Computing Settings:
* Computing Type: Forward Modeling
* Set *Save file prefix* (`shots.h5`) and *Output dir*
* Other settings may be changed by your choice

After settings are set something similar should be resulted:

```{image} fm_settings.png
:alt: Colada forward modeling settings
:class: bg-primary
:scale: 70%
:align: center
```

:::{note}

Muting is not supposed to be used with *Forward Modeling*.

:::

After calculations are done we can visualize model overlayed by computed shots (first shot for example):

```{image} modeled_shot.png
:alt: Colada modeled shot
:class: bg-primary
:scale: 70%
:align: center
```

## Reverse Time Migration (RTM)

To compute RTM first of all we need to set previously computed shots as geometry.

Then in *Computing Settings* set *Computing type: RTM*.

Set *Save file prefix* as *rtm.h5* and *Output dir* to Geo Volumes.

To achieve good results we should apply muting.
Basically we should mute water layer (412.5m) and turning waves (Data mute).
We will use model muting 412.5m without taper.
In *Mute data* set *mute turning*. 
*Mute t0* to 150ms (approximate wavelet length) and *Mute data velocity* to 1.5km/s (water velocity).

2D velocity model overlayed with RTM is shown below:

```{image} rtm.png
:alt: Colada rtm
:class: bg-primary
:scale: 70%
:align: center
```

:::{note}

In practice field data must contain only reflected waves (our data have both direct and reflected waves). 
Also in this example source step is too big (500m).
That is why the result is not clean.

:::

## Least-Squares Reverse Time Migration (LSRTM)

To run LSRTM select true velocity model as *Input*.
*Geometry* same generated shots.
In *Computing Settings* set *Save file prefix* to *lsrtm.h5* and *Output dir* to Geo Volumes.
Use same mutings that were used in conventional RTM and run.

```{image} rtm_lsrtm.png
:alt: Colada rtm and lsrtm
:class: bg-primary
:scale: 70%
:align: center
```

Residual norm and other convergence attribute may be found in created *lsrtm.h5* container (use HDFVIEW):

```{image} lsrtm_rnorm.png
:alt: Colada lsrtm residual norm
:class: bg-primary
:scale: 70%
:align: center
```

## Full Waveform Inversion (FWI)

As we know the goal of FWI is to make starting velocity model more precise.
Thus we need to set smoothed velocity model *model_2D_smooth* as input.
The geometry is the same shots that were used for RTM.
And in *Computing Settings* we need to set *Computing type: FWI*.
*Save file prefix* as *fwi.h5* and *Output dir* to Geo Volumes.
Model muting is 412.5m without taper.
We will not use *Data muting* but in practice FWI works with turnings waves.
And **important thing** is to turn on *Replace water velocity/density*. 
This will replace velocity (and density if present) at each iteration.

In *FWI Settings* set min/max velocities to 1000 and 3500 respectively.

After passing 10 iteration we may get result similar to shown below:

```{image} fwi.png
:alt: Colada fwi
:class: bg-primary
:scale: 70%
:align: center
```

At left is the smoothed starting model and at right - result of FWI 10th iteration.

To see the convergence we can copy values from *fhistory* dataset (open with HDFVIEW for example) and copy them to new table in *Tables* module. 
Then plot it.

```{image} fwi_convergence.png
:alt: Colada fwi convergence
:class: bg-primary
:scale: 70%
:align: center
```

Congratulations! 
We hope you enjoyed this tutorial.