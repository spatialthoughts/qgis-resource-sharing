from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingException,
    QgsFeatureRequest
)


class RecursiveNeighborSelection(QgsProcessingAlgorithm):
    INPUT = 'INPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                'Input Layer',
                types=[QgsProcessing.TypeVectorPolygon,
                QgsProcessing.TypeVectorLine
                ]
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)

        if not layer or not layer.isValid():
            raise QgsProcessingException("Invalid input layer.")

        selected_ids = layer.selectedFeatureIds()
        if not selected_ids:
            raise QgsProcessingException("No features selected. Please select one or more seed features.")

        visited = set()
        to_visit = set(selected_ids)

        def get_neighbors(feature):
            bbox = feature.geometry().boundingBox()
            neighbors = []
            request = QgsFeatureRequest(bbox)
            for f in layer.getFeatures(request):
                if f.id() != feature.id() and f.geometry().intersects(feature.geometry()):
                    neighbors.append(f.id())
            return neighbors

        while to_visit:
            current_id = to_visit.pop()
            if current_id in visited:
                continue
            visited.add(current_id)
            feature = layer.getFeature(current_id)
            neighbors = get_neighbors(feature)
            new_neighbors = set(neighbors) - visited
            to_visit.update(new_neighbors)

        layer.selectByIds(list(visited))
        feedback.pushInfo(f"{len(visited)} features selected from {len(selected_ids)} seed(s).")
        return {}

    def name(self):
        return 'recursive_neighbor_selection'

    def displayName(self):
        return 'Recursive Neighbor Selection'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return RecursiveNeighborSelection()
