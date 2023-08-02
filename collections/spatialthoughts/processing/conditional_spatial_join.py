from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingFeatureBasedAlgorithm, 
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsFeatureRequest,
                       QgsFields,
                       QgsField,
                       QgsFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsFeature, 
                       QgsWkbTypes)
    

class ConditionalSpatialJoin(QgsProcessingFeatureBasedAlgorithm):
    """
    This processing algorithm does a spatial join between an input polygon
    layer and a point join layer. It finds all intersecting points within each 
    polygon and transfer the chosen attribute based on values of another 
    attribute. 
    
    Example: Given a layer of urban areas and populated places, it can add the 
    name of the populated place having the highest population within each
    urban area.
    
    We are using QgsProcessingFeatureBasedAlgorithm which processes each
    feature independently and can result in faster processing.
    """
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConditionalSpatialJoin()

    def name(self):
        return 'conditional_spatial_join'

    def displayName(self):
        return self.tr('Conditional Spatial Join')

    def group(self):
        return self.tr('')

    def groupId(self):
        return ''

    def outputName(self):
        return self.tr('joined')
        
    def shortHelpString(self):
        return self.tr(
            'This algorithm joins a vector polygon layer with a point layer '
            'and adds an attribute from intersecting points based on value of '
            'values of another attribute.')
    
    def __init__(self):
        super().__init__()
    
    def inputLayerTypes(self):
        return [QgsProcessing.TypeVectorPolygon]
        
    def outputWkbType(self, input_wkb_type):
        return QgsWkbTypes.Polygon
        
    def initParameters(self, config=None):
        # An input feature source named INPUT
        # and output sink named OUTPUT is defined
        # by the parent class.
        # We define other parameters
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'JOIN',
                'Join Layer',
                [QgsProcessing.TypeVectorPoint]
                ))        
                
        self.addParameter(
            QgsProcessingParameterField(
                'JOINFIELD',
                'Join Attribute',
                None,
                'JOIN'
                ))

        self.addParameter(
            QgsProcessingParameterEnum(
                'CONDITION',
                'Join Condition',
                ['Highest', 'Lowest'],
                False,
                'HIGHEST'
                ))
                
        self.addParameter(
            QgsProcessingParameterField(
                'CONDITION_FIELD',
                'Condition Attribute',
                None,
                'JOIN'
                ))
                
                
    def prepareAlgorithm(self, parameters, context, feedback):
        self.input_layer = self.parameterAsSource(parameters, 'INPUT', context)
        self.join_layer = self.parameterAsSource(parameters, 'JOIN', context)
        self.join_field = self.parameterAsString(parameters, 'JOINFIELD', context)
        self.condition = self.parameterAsEnum(parameters, 'CONDITION', context)
        self.condition_field = self.parameterAsString(
            parameters, 'CONDITION_FIELD', context)
        
        # Warn if there is no spatial index
        if self.join_layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexNotPresent:
            feedback.pushWarning(self.tr(
                'No spatial index exists for input layer, '
                'performance will be severely degraded' ) )
        return super().prepareAlgorithm(parameters, context, feedback)
    
    def outputFields(self, fields):
        join_layer_fields = self.join_layer.fields()
        for f in join_layer_fields:
            if f.name() == self.join_field:
                new_field = f

        fields.append(new_field)
        return fields
        
    def processFeature(self, feature, context, feedback):
        geometry = feature.geometry()

        # Get all intersecting point features
        request = QgsFeatureRequest().setFilterRect(geometry.boundingBox())
        intersecting_features = [
          p
          for p in self.join_layer.getFeatures(request) 
          if p.geometry().intersects(geometry)
        ]
        if self.condition == 0:
            intersecting_features.sort(
                key=lambda x: x[self.condition_field], reverse=True)
        elif self.condition == 1:
            intersecting_features.sort(
                key=lambda x: x[self.condition_field], reverse=False)
        
        if intersecting_features:
            selected = intersecting_features[0]
            new_attribute_value = selected[self.join_field]
        else:
            new_attribute_value = None
        
        
        attributes = feature.attributes()
        attributes.append(new_attribute_value)
        
        # Create a new feature and set its attributes
        new_f = QgsFeature()
        new_f.setGeometry(geometry)
        new_f.setAttributes(attributes)
        return [new_f]