# IO and Visualization

Start by dowloading [Teapot dome 3D](https://wiki.seg.org/wiki/Teapot_dome_3D_survey) open source dataset.

Next we need to find information about spatial refernce used in downloaded data. 
For that go to `DataSets/GIS/CD files` and open `NPR3_BASEMAP.jpg` that shows the survey on the relief map. 
In the lower left corner there is a spatial reference and units:

```{image} teapot_crs.png
:alt: Teapot sps
:class: bg-primary
:scale: 70%
:align: center
```

## Application settings

In Colada application settings (`Toolbar menu->Edit->Application Settings`) `General` panel set default directories for the data.

```{image} colada_app_settings_default_dirs.png
:alt: Colada default dirs settings
:class: bg-primary
:scale: 70%
:align: center
```

In the `Units` panel set preffered length and temporal units. In my case those are `meter` and `millisecond`.

```{image} colada_app_settings_units.png
:alt: Colada units settings
:class: bg-primary
:scale: 70%
:align: center
```

Then go to the spatial reference panel and  find the appropriate one. 
It seems that `NAD27 / Wyoming East Central (EPSG:32056)` is the right choice. 
Set it using drag&drop.

```{image} colada_app_settings_crs.png
:alt: Colada spatial reference settings
:class: bg-primary
:scale: 70%
:align: center
```

## Read SEGY

SEGY is represented by 3D STACK (`Seismic/CD files/3D_Seismic/filt_mig.sgy`) and bunch of 2D STACK (`DataSets/Seismic/CD files/2D_Seismic`) datasets. 

In Colada SEGY STACK may be read as *Geo Volume* or as *Seismic* object. 
We will read it as Geo Volume first and then as Seismic.

### Read SEGY as Geo Volume

To open Geo Volume SEGY reader right-click on Geo Volume tree `Import->SEGY STACK`. 
Add SEGY files from `DataSets/Seismic/CD files/2D_Seismic/NormalizedMigrated_segy/` and `DataSets/Seismic/CD files/3D_Seismic/` directories.
Before reading SEGY don't forget to check trace headers.
For *Teapot Dome* the correct header offsets for INLINE, XLINE and X, Y are shown in the picture.

```{image} geo_volume_reader.png
:alt: Colada geo volume reader
:class: bg-primary
:scale: 70%
:align: center
```

:::{warning}

Geo Volume is a regular grid that can be represented by origin, orientation and spacings along each axis.

SEGY stack data may not strictly follow this.
In this case XY plane will be broken and in practice the user must be confident that the SEGY is represented as a cube or flat with regular spacings.

:::

There are few things that should be explained. 

First of all each geo-object has attribute `Domain`. 
Possible values are: `TWT` (Two Way Traveltime), `OWT` (One Way Traveltime), `TVD` (True Vertical Depth), `TVDSS` (True Vertical Depth Sub-Sea).

CRS (Coordinate Seference System or Spatial Reference System) highly desirable for every geo-object.

`Length units`, `Temporal units` necessary for all geo-objects. Uusually they are needed to define coordinates.

`Data units` necessary for some geo-objects like Map if it is in `TWT/OWT` domain. 
Or for Geo Volume if it is going to be used in wave-modeling as velocity model for example.
`Data units` defines units of the data, for example for a Map object it defines units of surface values. 
Or for Geo Volume it defines units of each scalar value of data (pressure for example or particle displacement).

*To be confident that your units are convertable one may use the* [web service](http://13.52.135.81/convert).

## Data visualization

After data is read it should appear in the Geo Volume tree.
As Geo Volume may be pretty big and not all the time the user wants to load oll data to the memory, after clicking on the checkbox the module will be switched to `GeoVolumes` where one can select a subset of the data to load.

```{image} geo_volume_tree_with_data.png
:alt: Colada geo volume tree with data
:class: bg-primary
:scale: 70%
:align: center
```

When the data is loaded new item will appear in *Subject Hierarchy* window.
To visualize Geo Volume one may click on *eye* picture like shown in the picture.

```{image} geo_volume_subj_hierarchy.png
:alt: Colada geo volume subject hierarchy
:class: bg-primary
:scale: 70%
:align: center
```

Geo Volume should be visualized.

By default *Slice Views* are synchronized.
One can disable taht by clicking on the *chain* button.

To see axes in Slice View one should change the preset to one of the following: `XY`, `YZ`, `XZ`.

```{image} geo_volume_displayed.png
:alt: Colada geo volume displayed
:class: bg-primary
:scale: 70%
:align: center
```

Further one can visualize two volumes one upon another.
To do that there is a place for *background* and *foreground* volumes.
Place 2D as background and 3D cuba as foreground.
Then using slicer change the opacty to see how these two objects relates.

```{image} slice_toolbar.png
:alt: Colada slice toolbar
:class: bg-primary
:scale: 70%
:align: center
```

Another way to visualize the data is to drag&drop the selected object to the scene.
In this case an object will be rendered as Volume.

```{image} volume_rendered.png
:alt: Colada volume rendered
:class: bg-primary
:scale: 70%
:align: center
```

Rendered Volume is controlled in `Volume Rendering` module.
`Volume` module is for usual representation using Slices.
Check these modules to see how you can customize the visualization.