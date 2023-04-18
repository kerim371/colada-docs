# Overview

Colada is a crossplatform desktop software that utilizes full power of C++, Python and Julia 
to make geological/geophysical data processing effective, fast and robust. 
Currently it only supports:
1) Data visualization (including pre/post stack seismic);
2) Various operations on data (like transforms, interpolation, interactive tools etc.);
3) 2D/3D seismic wavemodeling including scalar, acoustic, elastic, VTI/TTI models (Unix only);
4) 2D/3D Full Waveform Inversion (FWI), Reverse Time Migration (RTM), Least-Squares Reverse Time Migration (LSRTM) (Unix only);

Most functionality is implemented through extensions and modules. 
Modules are written on either C++ or Python. 
From the user side there is no any visible difference between C++ and Python modules. 
On the other hand use of Python ultimately reduces time of new functionality implementation. 
Many open source projects are involved and more are yet going to be involved. 

**The first great thing** about Colada is that it has all the modern visualization capabilities. 
It is not only about 2D/3D visualization that is ready to use but also the functionality that will be implemented in the near future like: Virtual Reality, Holographic Display and 3D printing.

**The second great thing** is that even the core is written in C++ all the functionality is available from embedded Python interpreter. 
Even Graphical User Interface! 
That grants almost unlimited abilities to the user with Python knowledge. 
Reading low-popular files, processing multiples files in loop without monotonic routine or adding new functionality is as simple as you familiar with Python. 

**The third great thing** is about large-scale problems. 
For such tasks there is Julia interpreter wich allows to write code as fast as using Python and be as efficient as C language. 
Best choice for mathematicians. 

All of this is based on core with over 20 years of history [Slicer 3D](https://www.slicer.org/) and the community that supports it.
