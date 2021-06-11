import requests
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
    QgsProcessingParameterFeatureSource, QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString, QgsProcessingParameterNumber, QgsWkbTypes,
    QgsGeometry, QgsFeatureSink, QgsFields, QgsPoint, QgsFeature)
from PyQt5.QtXml import QDomDocument
class ExportLayoutAlgorithm(QgsProcessingAlgorithm):
    """Exports the current map view to PDF"""
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SERVICE = 'SERVICE'
    TOLERANCE = 'TOLERANCE'
     
    def flags(self):
          return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Input vector layer'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )
         
        self.addParameter(
            QgsProcessingParameterString(
                self.SERVICE,
                self.tr('OSRM Service URL'),
                'http://127.0.0.1:5000'
            )
        )
         
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Snapping Tolerance (meters)'),
                QgsProcessingParameterNumber.Integer,
                10
            )
        )
         
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Snapped Line',
                QgsProcessing.TypeVectorLine
            )
        )
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        service = self.parameterAsString(parameters, self.SERVICE, context)
        tolerance = self.parameterAsInt(parameters, self.TOLERANCE, context)
         
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            QgsFields(),
            QgsWkbTypes.LineString,
            source.sourceCrs()
            )
         
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
         
        coordinate_list = []
        for current, f in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            geom = f.geometry().asPoint()
            coordinates = '{},{}'.format(geom.x(), geom.y())
            coordinate_list.append(coordinates)
            feedback.setProgress(int(current * total))
        coordinate_str = ';'.join(coordinate_list)
        radius = ['{}'.format(tolerance)]
        radius_str = ';'.join(radius*len(coordinate_list))
        service_url = '/match/v1/driving/{}'.format(coordinate_str)
        request_url = service + service_url
        payload = {'geometries': 'geojson', 'steps': 'false', 'radiuses': radius_str}
        r = requests.get(request_url, params=payload)
        results = r.json()
         
        for match in results['matchings']:
            coords = match['geometry']['coordinates']
            point_list = [QgsPoint(coord[0], coord[1]) for coord in coords]
            out_f = QgsFeature()
            out_f.setGeometry(QgsGeometry.fromPolyline(point_list))
            sink.addFeature(out_f, QgsFeatureSink.FastInsert)
             
        return {self.OUTPUT: sink} 
    def name(self):
        return 'snap_to_roads'
    def displayName(self):
        return self.tr('Snap to Roads')
         
    def shortHelpString(self):
        return self.tr('Snaps GPS Trackpoints to OSM roads using OSRM service')
    def group(self):
        return self.tr(self.groupId())
    def groupId(self):
        return ''
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    def createInstance(self):
        return ExportLayoutAlgorithm()