from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
import rig_factory.environment as env


class HairNetwork(Transform):

    hair_system = ObjectProperty(
        name='hair_system'
    )

    follicle_group = ObjectProperty(
        name='follicle_group'
    )

    curve_group = ObjectProperty(
        name='curve_group'
    )

    curves = ObjectListProperty(
        name='curves'
    )

    follicles = ObjectListProperty(
        name='follicles'
    )

    nucleus = ObjectProperty(
        name='nucleus'
    )

    def __init__(self, *args, **kwargs):
        super(HairNetwork, self).__init__(*args, **kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(HairNetwork, cls).create(controller, **kwargs)

        root_name = this.root_name

        this.hair_system = this.create_child(
            DagNode,
            node_type='hairSystem'
        )
        if this.nucleus:
            index = this.nucleus.plugs['inputActive'].get_next_avaliable_index()
            this.nucleus.plugs['startFrame'].connect_to(this.hair_system.plugs['startFrame'])
            this.hair_system.plugs['currentState'].connect_to(this.nucleus.plugs['inputActive'].element(index))
            this.hair_system.plugs['startState'].connect_to(this.nucleus.plugs['inputActiveStart'].element(index))
            this.nucleus.plugs['outputObjects'].element(index).connect_to(this.hair_system.plugs['nextState'])

        this.follicle_group = this.create_child(
            Transform,
            root_name='%s_follicles' % root_name
        )
        this.curve_group = this.create_child(
            Transform,
            root_name='%s_curves' % root_name
        )
        controller.scene.connectAttr('time1.outTime', '%s.currentTime' % this.hair_system)

        this.follicle_group.plugs.set_values(
            inheritsTransform=False
        )
        this.curve_group.plugs.set_values(
            inheritsTransform=False
        )

        color = env.colors[this.side]
        this.plugs['overrideEnabled'].set_value(True)
        this.plugs['overrideRGBColors'].set_value(True)
        this.plugs['overrideColorR'].set_value(color[0])
        this.plugs['overrideColorG'].set_value(color[1])
        this.plugs['overrideColorB'].set_value(color[2])

        return this


hair_system_attrs = [u'simulationMethod', u'collide', u'collideStrength', u'collideOverSample', u'selfCollide',
                     u'collideGround', u'groundHeight', u'collisionFlag', u'selfCollisionFlag', u'collisionLayer',
                     u'stretchResistance',
                     u'compressionResistance', u'restLengthScale', u'twistResistance', u'bendResistance',
                     u'extraBendLinks', u'stiffness',
                     u'stiffnessScale', u'stiffnessScale.stiffnessScale_Position',
                     u'stiffnessScale.stiffnessScale_FloatValue',
                     u'stiffnessScale.stiffnessScale_Interp', u'lengthFlex', u'damp', u'stretchDamp', u'drag',
                     u'tangentialDrag', u'friction',
                     u'stickiness', u'bounce', u'mass', u'dynamicsWeight', u'collideWidthOffset',
                     u'selfCollideWidthScale', u'staticCling',
                     u'repulsion', u'numCollideNeighbors', u'maxSelfCollisionIterations', u'iterations',
                     u'drawCollideWidth', u'widthDrawSkip',
                     u'ignoreSolverGravity', u'ignoreSolverWind', u'gravity', u'turbulenceStrength',
                     u'turbulenceFrequency', u'turbulenceSpeed',
                     u'attractionDamp', u'startCurveAttract', u'motionDrag', u'displayQuality', u'noStretch',
                     u'subSegments', u'clumpWidth',
                     u'clumpWidthScale', u'clumpWidthScale.clumpWidthScale_Position',
                     u'clumpWidthScale.clumpWidthScale_FloatValue',
                     u'clumpWidthScale.clumpWidthScale_Interp', u'clumpTwist', u'clumpCurl',
                     u'clumpCurl.clumpCurl_Position',
                     u'clumpCurl.clumpCurl_FloatValue', u'clumpCurl.clumpCurl_Interp', u'clumpFlatness',
                     u'clumpFlatness.clumpFlatness_Position',
                     u'clumpFlatness.clumpFlatness_FloatValue', u'clumpFlatness.clumpFlatness_Interp', u'bendFollow',
                     u'hairWidth',
                     u'hairWidthScale', u'hairWidthScale.hairWidthScale_Position',
                     u'hairWidthScale.hairWidthScale_FloatValue',
                     u'hairWidthScale.hairWidthScale_Interp', u'baldnessMap', u'opacity', u'hairColorR', u'hairColorG',
                     u'hairColorB',
                     u'hairColorScale', u'hairColorScale.hairColorScale_Position',
                     u'hairColorScale.hairColorScale_Color',
                     u'hairColorScale.hairColorScale_ColorR', u'hairColorScale.hairColorScale_ColorG',
                     u'hairColorScale.hairColorScale_ColorB',
                     u'hairColorScale.hairColorScale_Interp', u'hairsPerClump', u'thinning', u'translucence',
                     u'specularColorR',
                     u'specularColorG', u'specularColorB', u'specularPower', u'castShadows', u'diffuseRand',
                     u'specularRand', u'hueRand',
                     u'satRand', u'valRand', u'multiStreaks', u'multiStreakSpread1', u'multiStreakSpread2',
                     u'lightEachHair', u'displacementScale',
                     u'displacementScale.displacementScale_Position', u'displacementScale.displacementScale_FloatValue',
                     u'displacementScale.displacementScale_Interp', u'curl', u'curlFrequency', u'noiseMethod', u'noise',
                     u'detailNoise',
                     u'noiseFrequency', u'noiseFrequencyU', u'noiseFrequencyV', u'noiseFrequencyW', u'subClumpMethod',
                     u'subClumping',
                     u'subClumpRand', u'numUClumps', u'numVClumps', u'clumpInterpolation', u'interpolationRange',
                     u'currentTime', u'startFrame',
                     u'usePre70ForceIntensity', u'disableFollicleAnim', u'playFromCache', u'displayColorR',
                     u'displayColorG', u'displayColorB',
                     u'attractionScale', u'attractionScale.attractionScaleScale_Position',
                     u'attractionScale.attractionScale_FloatValue',
                     u'attractionScale.attractionScale_Interp']
