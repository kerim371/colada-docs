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

## Adjust application settings

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
Add files 