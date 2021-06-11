import networkx as nx
import numpy as np
from itertools import groupby
from PyQt5.QtCore import QCoreApplication, QVariant

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
    QgsProcessingParameterFeatureSource, QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,QgsFields, QgsField, QgsWkbTypes,
    QgsFeatureSink, QgsProcessingUtils)


class ConstrainedKMeansAlgorithm(QgsProcessingAlgorithm):
    """Calculates the 2D distance based k-means cluster number for each input feature"""
    INPUT = 'INPUT'
    CLUSTERS = 'CLUSTERS'
    MINPOINTS = 'MINPOINTS'
    OUTPUT = 'OUTPUT'

    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Input Layer'),
                types=[QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                'CLUSTERS',
                self.tr('Number of Clusters'),
                QgsProcessingParameterNumber.Integer,
                5, False, 1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                'MINPOINTS',
                self.tr('Miminum Number of Points per Cluster'),
                QgsProcessingParameterNumber.Integer,
                1, False, 1
            )
        )
        
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Clusters',
                QgsProcessing.TypeVectorAnyGeometry
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source= self.parameterAsSource(parameters, self.INPUT, context)
        k = self.parameterAsInt(parameters, self.CLUSTERS, context)
        minpoints = self.parameterAsInt(parameters, self.MINPOINTS, context)
        
        outputFields = source.fields()
        newFields = QgsFields()
        newFields.append(QgsField('CLUSTER_ID', QVariant.Int))
        newFields.append(QgsField('CLUSTER_SIZE', QVariant.Int))

        outputFields = QgsProcessingUtils.combineFields(outputFields, newFields)
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            outputFields,
            source.wkbType(),
            source.sourceCrs()
            )
        feedback.pushInfo(self.tr( "Collecting input points"))
        
        features = [f for f in source.getFeatures()]
        data = []
        for f in features:
            geometry = f.geometry()
            if geometry.wkbType() == QgsWkbTypes.Point:
                point = geometry
            else:
                point = geometry.centroid()
            
            data.append([point.asPoint().x(), point.asPoint().y()])
        
        feedback.pushInfo(self.tr( "Input ready"))
        feedback.pushInfo(self.tr( "Computing clusters"))

        demand = [minpoints] * k
        C, M, f = constrained_kmeans(data, demand, maxiter=5)
        feedback.pushInfo(self.tr( "Clusters ready"))

        # M is the cluster assignment for the data points
        # Compute cluster sizes
        sorted_M = np.sort(M)
        sizes = [len(list(group)) for key, group in groupby(sorted_M)]
    
        
        for index, out_f in enumerate(features):
            attributes = out_f.attributes()
            cluster_id = M[index].item()
            attributes.append(cluster_id + 1)
            attributes.append(sizes[cluster_id])

            out_f.setAttributes(attributes)
            sink.addFeature(out_f, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: sink} 

    def name(self):
        return 'constrained_kmeans'

    def displayName(self):
        return self.tr('Constrained K-Means Clustering')
        
    def shortHelpString(self):
        return self.tr('Constrained K-Means Clustering algorithm PyQGIS implementation')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConstrainedKMeansAlgorithm()

# Code adapted from https://adared.ch/constrained-k-means-implementation-in-python/
def constrained_kmeans(data, demand, maxiter=None, fixedprec=1e9):
  data = np.array(data)
  
  min_ = np.min(data, axis = 0)
  max_ = np.max(data, axis = 0)
  
  C = min_ + np.random.random((len(demand), data.shape[1])) * (max_ - min_)
  M = np.array([-1] * len(data), dtype=np.int)
  
  itercnt = 0
  while True:
    itercnt += 1
    print(data)
    print(itercnt)
    # memberships
    g = nx.DiGraph()
    g.add_nodes_from(range(0, data.shape[0]), demand=-1) # points
    for i in range(0, len(C)):
      g.add_node(len(data) + i, demand=demand[i])
    # Calculating cost...
    print('Cost')
    cost = np.array([np.linalg.norm(np.tile(data.T, len(C)).T - np.tile(C, len(data)).reshape(len(C) * len(data), C.shape[1]), axis=1)])
    # Preparing data_to_C_edges...
    data_to_C_edges = np.concatenate((np.tile([range(0, data.shape[0])],
    len(C)).T, np.tile(np.array([range(data.shape[0], data.shape[0] +
    C.shape[0])]).T, len(data)).reshape(len(C) * len(data), 1), cost.T *
    fixedprec), axis=1).astype(np.uint64) # Adding to graph
    g.add_weighted_edges_from(data_to_C_edges)
    

    a = len(data) + len(C)
    g.add_node(a, demand=len(data)-np.sum(demand))
    C_to_a_edges = np.concatenate((np.array([range(len(data), len(data) + len(C))]).T, np.tile([[a]], len(C)).T), axis=1)
    g.add_edges_from(C_to_a_edges)
    
    print('Flow')
    # Calculating min cost flow...
    f = nx.min_cost_flow(g)
    print('Flow Done')
    # assign
    M_new = np.ones(len(data), dtype=np.int) * -1
    for i in range(len(data)):
      p = sorted(f[i].items(), key=lambda x: x[1])[-1][0]
      M_new[i] = p - len(data)
      
    # stop condition
    if np.all(M_new == M):
      # Stop
      return (C, M, f)
      
    M = M_new
      
    # compute new centers
    for i in range(len(C)):
      C[i, :] = np.mean(data[M==i, :], axis=0)
      
    if maxiter is not None and itercnt >= maxiter:
      # Max iterations reached
      return (C, M, f)