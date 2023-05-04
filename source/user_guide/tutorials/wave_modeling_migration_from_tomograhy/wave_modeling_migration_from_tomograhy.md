# Wave Modeling: 1994 BP migration from topography dataset

Before getting started one should download velocity model from [SEG page](https://wiki.seg.org/wiki/1994_BP_migration_from_topography).

## Reading data

Velocity model is represented by SEGY file.
One should read it as Geo Volume: right click on *Geo Volume treeview -> Import -> SEGY STACK*.
Read parameters:
1) Domain: *TVD*
2) Length units: *decimeter* (use [this service](https://units.readthedocs.io/en/latest/_static/convert.html) to check whether units can be converted to any other)
3) Data units: *m/s*
4) Samp rate: *-100*
5) Byte start: IL: *17*
5) Byte start: XL: *9*
6) Byte start: X: *73*
7) Byte start: Y: *77*

```{image} reader.png
:alt: reader
:class: bg-primary
:scale: 60%
:align: center
```

:::{warning}

As some trace headers are incorrect in this SEGY (see few last traces) most likely volume parameters (origin, spacings) should be manually fixed then.
For that after SEGY is read go to the *Geo Volumes* module and select volume read.
Make sure that origin is [0,0,-99900] and spacings are [150, 1, 100] decimeters.
After setting this and clicking *Update* button the velocity model is ready.

:::

## Generating geometry

From data description geometry should contain 277 shots with 90m interval.
480 traces per shot spread from -3600m to 3600m with 15m interval.
Receivers are moved along with source.
Sampling rate is 4 ms, number of samples 1000.

In Colada geometry is Seis object.
Thus go to the *Seismic* module and create new seismic with parameters:
1) Data type: *PRESTACK*
2) Survey type: *TWO_D*
3) Domain: *TWT*
4) Number of traces: let it be *480* (will be changed anyway)
5) Number of samples: *1000*
6) Sampling rate: *4*
7) Trace chunking: *480* (see [HDF5 chunking](https://support.hdfgroup.org/HDF5/doc/Advanced/Chunking/))
8) length units: *m*
9) Temporal units: *ms*

Click *Create* button.

Then in the *Geometry* section set:
1) Source geometry x0,dx,nx: *0,90,277*
2) Receiver geometry x0,dx,nx: *-3600,15,480*
3) Check on *move receivers with sources*

Click *Generate Geometry* button.

## Forward modeling

Go to the *Wave Modeling* module.
Set velocity model as input.
Generated geometry as *Field Records (Geometry)*

Modeling settings:
1) Computing type: *Forward modeling*
2) Ricker frequency: *0.02* kHz
3) Select *Save file prefix* and *Output dir*

Click *Start Computing*.

:::{note}

It is recommended to always compute one or small number of shots before starting computation on all shots.
This allows to check if the solution is accurate enough or not and make changes to settings.
For that in *Additional settings* set *Compute each Nth shot* to some big number.

:::

After computations are done one can see the result, for example this is 129 shot:

```{image} shot_129.png
:alt: 129 shot
:class: bg-primary
:scale: 70%
:align: center
```

## Reverse Time Migration (RTM)

RTM works with field data thus geometry input file must be replaced by the computed synthetic records.

Then in *Common computing settings*:
1) Computing type: *RTM*
2) Limit modeling domain: *0* (if set to 3000 then about 35 Gb RAM is required)
3) Change *Save file prefix* and *Output dir* (the result will be Geo Volume)

and in *A*dditional settings*:
1) Mute model: *On*
2) Mute model (m): *170*
3) Mute model taper (m): *10*
4) Mute data: *mute turning* (upper triangle mute)
5) Mute data start time (t0,ms): *140* (approximate length of a 20 Hz Ricker signal)
6) Mute data velocity (km/s): *4*

Click *Start Computing*

The result may be similar to this:

```{image} rtm.png
:alt: rtm
:class: bg-primary
:scale: 70%
:align: center
```

and this is velocity model overlayed by RTM:

```{image} model_overlayed_with_rtm.png
:alt: velocity model overlayed by rtm
:class: bg-primary
:scale: 70%
:align: center
```

Hope you liked it.