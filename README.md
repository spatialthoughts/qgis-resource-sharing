# SpatialThoughts QGIS Resources

This repository contains scripts, models and other QGIS resources that can be used from the [QGIS Resource Sharing](https://plugins.qgis.org/plugins/qgis_resource_sharing/) plugin

## Resources

### Models

[See all models](https://github.com/spatialthoughts/qgis-resource-sharing/tree/main/collections/spatialthoughts/models)

1. *Spatial Homogeniety Test*: Processing model for [Spatial Homogeneity Testing of Raingauge Data with Advanced QGIS Expressions](https://spatialthoughts.com/2020/11/26/spatial-homogeneity-testing-qgis/)
2. *Split Polygons*: Processing model for [Split Polygons into Equal Parts using QGIS](https://spatialthoughts.com/2021/06/12/split-polygons-qgis/)
3. *Connect to Nearest Node*: Processing model demonstrating a solution for [Spatial Analysis Challenge: Connect Buildings to Nearest Point on the Road](https://www.youtube.com/watch?v=7V8-JaiABTQ).
4. *Smooth Polygons*: Processing model to smooth voronoi polygons.
5. *Fix Transects*: Processing model demonstration a solution for [Spatial Analysis Challenge: Fix Line Transects](https://www.youtube.com/watch?v=RRAT_PIow4Q)

[See all scripts](https://github.com/spatialthoughts/qgis-resource-sharing/tree/main/collections/spatialthoughts/scripts)

### Scripts

1. Constrained K-Means Clustering: Processing script for [K-Means Clustering with Equal Sized Clusters in QGIS](https://spatialthoughts.com/2021/01/31/equal-sized-kmeans-qgis/)
2. Equidistance Buffer: Processing script for [Approximating Geodesic Buffers in QGIS](https://spatialthoughts.com/2019/04/05/geodesic-buffers-in-qgis/)
3. Snap to Roads: Processing script for [Snapping GPS tracks to Roads using QGIS and OSRM](https://spatialthoughts.com/2020/02/22/snap-to-roads-qgis-and-osrm/)
4. Attribute Iterator: Processing script to iterate over all attributes of a vector layer and create an Attribute Index.
5. Conditional Spatial Join: Processing script to do a spatial join and aggregate features based on a condition. [video explanation](https://www.youtube.com/watch?v=qpiFT8UHhwM)

   
## Installation

1. Install the [QGIS Resource Sharing](https://plugins.qgis.org/plugins/qgis_resource_sharing/) plugin. 
<img width="50%" alt="resource_sharing1" src="https://user-images.githubusercontent.com/5227506/121690798-eeef9e00-cae3-11eb-8f33-9995d50fae04.png">

2. Once installed, launch the plugin from Plugins &rarr; Resource Sharing &rarr; Resource Sharing. Switch to the *Settings* tab and click *Add Repository*.
  <img width="50%" alt="resource_sharing2" src="https://user-images.githubusercontent.com/5227506/121691047-2d855880-cae4-11eb-82e7-edaa29ab7916.png">

3. Name the repositry as `Spatial Thoughts Resources` and enter the URL as `https://github.com/spatialthoughts/qgis-resource-sharing.git`
<img width="50%" alt="resource_sharing3" src="https://user-images.githubusercontent.com/5227506/121691160-50b00800-cae4-11eb-9a55-c679d7b9a73e.png">

4. Switch to the *All Collections* tab and search for `SpatialThoughts`. Once you find the collection, click *Install*.

<img width="50%" alt="resource_sharing4" src="https://user-images.githubusercontent.com/5227506/121691168-5279cb80-cae4-11eb-9755-61fe2d7c4be5.png">

5. Once installed, you will see new *Models* and *Scripts* in your Processing Toolbox.
  <img width="50%" alt="resource_sharing5" src="https://user-images.githubusercontent.com/5227506/121691179-54438f00-cae4-11eb-8452-5bd6631662aa.png">

