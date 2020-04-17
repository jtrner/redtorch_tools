from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.base_objects.base_object import BaseObject

# Node Objects
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh, MeshVertex
from rig_factory.objects.node_objects.connection import Connection
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.shader import Shader
from rig_factory.objects.node_objects.shading_group import ShadingGroup
from rig_factory.objects.node_objects.object_set import ObjectSet
from rig_factory.objects.node_objects.animation_curve import AnimationCurve
from rig_factory.objects.node_objects.keyframe import KeyFrame
from rig_factory.objects.node_objects.ik_handle import IkEffector, IkHandle
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle

# Blendshape Objects
from rig_factory.objects.blendshape_objects.blendshape import (
    BlendshapeInbetween, BlendshapeGroup, Blendshape, BlendshapeTarget
)

# Face Network Objects

from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects.face_network import FaceNetwork

# Part Objects
from rig_factory.objects.part_objects.layered_ribbon_chain import LayeredRibbonChain, LayeredRibbonChainGuide
from rig_factory.objects.part_objects.ribbon_chain import RibbonChain, RibbonChainGuide
from rig_factory.objects.part_objects.ribbon_chain import RibbonChain, RibbonChainGuide

from rig_factory.objects.part_objects.follicle_handle import FollicleHandleGuide, FollicleHandle
from rig_factory.objects.part_objects.main import MainGuide, Main
from rig_factory.objects.part_objects.eye_brow_part import EyebrowPart, EyebrowPartGuide
from rig_factory.objects.part_objects.wire_part import WirePart, WirePartGuide
from rig_factory.objects.part_objects.single_world_handle_part import SingleWorldHandle, SingleWorldHandleGuide


# Biped Objects
from rig_factory.objects.biped_objects.biped_arm_ik import BipedArmIkGuide, BipedArmIk
from rig_factory.objects.biped_objects.biped_arm_fk import BipedArmFkGuide, BipedArmFk
from rig_factory.objects.biped_objects.biped_arm import BipedArmGuide, BipedArm
from rig_factory.objects.biped_objects.biped_arm_bendy import BipedArmBendyGuide, BipedArmBendy
from rig_factory.objects.biped_objects.biped_leg_ik import BipedLegIkGuide, BipedLegIk
from rig_factory.objects.biped_objects.biped_leg_fk import BipedLegFkGuide, BipedLegFk
from rig_factory.objects.biped_objects.biped_leg import BipedLegGuide, BipedLeg
from rig_factory.objects.biped_objects.biped_leg_bendy import BipedLegBendyGuide, BipedLegBendy
from rig_factory.objects.biped_objects.biped_spine import BipedSpineGuide, BipedSpine
from rig_factory.objects.biped_objects.biped_spine_fk import BipedSpineFkGuide, BipedSpineFk
from rig_factory.objects.biped_objects.biped_spine_ik import BipedSpineIkGuide, BipedSpineIk
from rig_factory.objects.biped_objects.biped_neck_ik import BipedNeckIkGuide, BipedNeckIk
from rig_factory.objects.biped_objects.biped_neck_fk import BipedNeckFkGuide, BipedNeckFk
from rig_factory.objects.biped_objects.biped_neck_fk_spline import BipedNeckFkSplineGuide, BipedNeckFkSpline
from rig_factory.objects.biped_objects.biped_neck_fk2 import BipedNeckFkGuide2, BipedNeckFk2
from rig_factory.objects.biped_objects.biped_neck import BipedNeckGuide, BipedNeck
from rig_factory.objects.biped_objects.biped import BipedGuide, Biped
from rig_factory.objects.biped_objects.biped_main import BipedMainGuide, BipedMain
from rig_factory.objects.biped_objects.biped_hand import BipedHand, BipedHandGuide
from rig_factory.objects.biped_objects.biped_finger import BipedFinger, BipedFingerGuide
from rig_factory.objects.biped_objects.eye import Eye, EyeGuide
from rig_factory.objects.biped_objects.eye_array import EyeArrayGuide, EyeArray
from rig_factory.objects.biped_objects.projection_eyes import ProjectionEyes, ProjectionEyesGuide
from rig_factory.objects.biped_objects.jaw import Jaw, JawGuide
from rig_factory.objects.biped_objects.jaw_new import NewJaw, NewJawGuide

# Face Objects
from rig_factory.objects.face_objects.face import FaceGuide, Face
from rig_factory.objects.face_objects.face_handle_array import FaceHandleArrayGuide, FaceHandleArray
from rig_factory.objects.face_objects.face_handle import FaceHandle, FaceHandleGuide
from rig_factory.objects.part_objects.eyelash_part import EyeLashPart, EyeLashPartGuide


# Face Panel Objects
from rig_factory.objects.face_panel_objects.brow_slider import BrowSlider, BrowSliderGuide
from rig_factory.objects.face_panel_objects.cheek_slider import CheekSlider, CheekSliderGuide
from rig_factory.objects.face_panel_objects.eye_slider import EyeSlider, EyeSliderGuide
from rig_factory.objects.face_panel_objects.mouth_slider import MouthSlider, MouthSliderGuide
from rig_factory.objects.face_panel_objects.nose_slider import NoseSlider, NoseSliderGuide
from rig_factory.objects.face_panel_objects.teeth_slider import TeethSlider, TeethSliderGuide
from rig_factory.objects.face_panel_objects.face_panel import FacePanelGuide, FacePanel
from rig_factory.objects.face_panel_objects.brow_waggle_slider import BrowWaggleSlider, BrowWaggleSliderGuide
from rig_factory.objects.face_panel_objects.blink_slider import BlinkSlider, BlinkSliderGuide
from rig_factory.objects.face_panel_objects.jaw_overbite_slider import JawOverbiteSlider, JawOverbiteSliderGuide
from rig_factory.objects.face_panel_objects.lip_sync_slider import LipSyncSlider, LipSyncSliderGuide
from rig_factory.objects.face_panel_objects.squash_slider import SquashSlider, SquashSliderGuide
from rig_factory.objects.face_panel_objects.tongue_slider import TongueSlider, TongueSliderGuide
from rig_factory.objects.face_panel_objects.lip_curl_slider import LipCurlSlider, LipCurlSliderGuide
from rig_factory.objects.face_panel_objects.face_panel_main_slider import FacePanelMain, FacePanelMainGuide
from rig_factory.objects.face_panel_objects.curve_slider import CurveSlider, CurveSliderGuide
from rig_factory.objects.face_panel_objects.split_shape_slider import SplitShapeSlider, SplitShapeSliderGuide
from rig_factory.objects.face_panel_objects.mouth_combo_slider import MouthComboSliderGuide, MouthComboSlider
from rig_factory.objects.face_panel_objects.vertical_slider import VerticalSlider, VerticalSliderGuide
from rig_factory.objects.face_panel_objects.eyelid_slider import EyeLidSlider, EyeLidSliderGuide
from rig_factory.objects.face_panel_objects.closed_blink_slider import ClosedBlinkSlider, ClosedBlinkSliderGuide
from rig_factory.objects.face_panel_objects.closed_eye_slider import ClosedEyeSlider, ClosedEyeSliderGuide


# Part Objects
from rig_factory.objects.part_objects.container import ContainerGuide, Container
from rig_factory.objects.part_objects.fk_chain import FkChainGuide, FkChain
from rig_factory.objects.part_objects.ik_chain import IkChain, IkChainGuide
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.part_objects.squash_part import SquashPart, SquashPartGuide
from rig_factory.objects.part_objects.bend_part import BendPart, BendPartGuide
from rig_factory.objects.part_objects.twist_part import TwistPart, TwistPartGuide
from rig_factory.objects.part_objects.nonlinear_part import NonlinearPart, NonlinearPartGuide
from rig_factory.objects.part_objects.new_nonlinear_part import NewNonlinearPart, NewNonlinearPartGuide
from rig_factory.objects.part_objects.simple_squash_part import SimpleSquashPart, SimpleSquashPartGuide
from rig_factory.objects.part_objects.wave_part import WavePart, WavePartGuide
from rig_factory.objects.part_objects.lattice_part import LatticePart, LatticePartGuide
from rig_factory.objects.part_objects.simple_lattice_part import SimpleLatticePart, SimpleLatticePartGuide
from rig_factory.objects.part_objects.layered_ribbon_spline_chain import LayeredRibbonSplineChain, LayeredRibbonSplineChainGuide
from rig_factory.objects.part_objects.simple_ribbon import SimpleRibbon, SimpleRibbonGuide
from rig_factory.objects.part_objects.squish_part import SquishPart, SquishPartGuide
from rig_factory.objects.part_objects.handle import Handle, HandleGuide
from rig_factory.objects.part_objects.handle_array import HandleArray, HandleArrayGuide
from rig_factory.objects.part_objects.screen_handle_part import ScreenHandlePart, ScreenHandlePartGuide
from rig_factory.objects.part_objects.post_script import PostScriptGuide, PostScript
from rig_factory.objects.part_objects.visibility_part import VisibilityGuide, Visibility
from rig_factory.objects.part_objects.bend_part import BendPart, BendPartGuide
from rig_factory.objects.part_objects.squash_part import SquashPart, SquashPartGuide
from rig_factory.objects.part_objects.squish_part import SquishPart, SquishPartGuide
from rig_factory.objects.part_objects.teeth import TeethGuide, Teeth
from rig_factory.objects.part_objects.environment import EnvironmentGuide, Environment
from rig_factory.objects.part_objects.prop import PropGuide, Prop
from rig_factory.objects.part_objects.character import CharacterGuide, Character
from rig_factory.objects.part_objects.vehicle import Vehicle, VehicleGuide

# Rig Objects

from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.driven_curve import DrivenCurve
from rig_factory.objects.rig_objects.constraint import Constraint, ParentConstraint, AimConstraint, PointConstraint, \
    OrientConstraint, TangentConstraint, PoleVectorConstraint, ScaleConstraint
from rig_factory.objects.rig_objects.guide_handle import GuideHandle, BoxHandleGuide
from rig_factory.objects.rig_objects.capsule import Capsule
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle, StandardHandle, GimbalHandle
from rig_factory.objects.rig_objects.space_switcher import SpaceSwitcher
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_factory.objects.rig_objects.matrix_space_switcher import MatrixSpaceSwitcher
from rig_factory.objects.rig_objects.matrix_constraint import ParentMatrixConstraint, PointMatrixConstraint, \
    OrientMatrixConstraint
from rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
from rig_factory.objects.rig_objects.text_curve import TextCurve
from rig_factory.objects.rig_objects.surface_point import SurfacePoint


# SDK Objects

from rig_factory.objects.sdk_objects.driven_plug import DrivenPlug
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.sdk_objects.sdk_curve import SDKCurve
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.sdk_objects.sdk_keyframe import SDKKeyFrame
from rig_factory.objects.sdk_objects.driven_plug import DrivenPlug
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork


#Slider Objects

from rig_factory.objects.slider_objects.quad_slider import QuadSlider, QuadSliderGuide
from rig_factory.objects.slider_objects.double_slider import DoubleSlider, DoubleSliderGuide
from rig_factory.objects.slider_objects.brow_slider_array import BrowSliderArray, BrowSliderArrayGuide
from rig_factory.objects.slider_objects.mouth_slider_array import MouthSliderArray, MouthSliderArrayGuide

# Standard Biped Objects

'''
from rig_factory.objects.standard_biped_objects.standard_bendy_leg import StandardBendyLegGuide, StandardBendyLeg
from rig_factory.objects.standard_biped_objects.standard_bendy_arm import StandardBendyArmGuide, StandardBendyArm
from rig_factory.objects.standard_biped_objects.standard_fk_leg import StandardFKLegGuide, StandardFKLeg
from rig_factory.objects.standard_biped_objects.standard_ik_leg import StandardIKLegGuide, StandardIKLeg
from rig_factory.objects.standard_biped_objects.standard_leg import StandardLegGuide, StandardLeg
from rig_factory.objects.standard_biped_objects.twisty_leg import TwistyLegGuide, TwistyLeg
from rig_factory.objects.standard_biped_objects.standard_fk_arm import StandardFKArmGuide, StandardFKArm
from rig_factory.objects.standard_biped_objects.standard_ik_arm import StandardIKArmGuide, StandardIKArm
from rig_factory.objects.standard_biped_objects.standard_arm import StandardArmGuide, StandardArm
from rig_factory.objects.standard_biped_objects.standard_spine import StandardSpineGuide, StandardSpine
from rig_factory.objects.standard_biped_objects.standard_bendy_spine import StandardBendySpineGuide, StandardBendySpine
from rig_factory.objects.standard_biped_objects.standard_bendy_neck import StandardBendyNeckGuide, StandardBendyNeck
from rig_factory.objects.standard_biped_objects.bendy_spline import BendySplineGuide, BendySpline
from rig_factory.objects.standard_biped_objects.bendy_spline import BendySplineGuide, BendySpline
from rig_factory.objects.standard_biped_objects.head_squash_and_stretch import HeadGuide, Head
'''

# Quadruped Objects
from rig_factory.objects.quadruped_objects.quadruped import QuadrupedGuide, Quadruped
from rig_factory.objects.quadruped_objects.quadruped_spine import QuadrupedSpineGuide, QuadrupedSpine
from rig_factory.objects.quadruped_objects.quadruped_spine_ik import QuadrupedSpineIk, QuadrupedSpineIkGuide
from rig_factory.objects.quadruped_objects.quadruped_spine_fk import QuadrupedSpineFk, QuadrupedSpineFkGuide
from rig_factory.objects.quadruped_objects.quadruped_front_leg_fk import QuadrupedFrontLegFk, QuadrupedFrontLegFkGuide
from rig_factory.objects.quadruped_objects.quadruped_front_leg_ik import QuadrupedFrontLegIk, QuadrupedFrontLegIkGuide
from rig_factory.objects.quadruped_objects.quadruped_front_leg import QuadrupedFrontLegGuide, QuadrupedFrontLeg
from rig_factory.objects.quadruped_objects.quadruped_back_leg_fk import QuadrupedBackLegFk, QuadrupedBackLegFkGuide
from rig_factory.objects.quadruped_objects.quadruped_back_leg_ik import QuadrupedBackLegIk, QuadrupedBackLegIkGuide
from rig_factory.objects.quadruped_objects.quadruped_back_leg import QuadrupedBackLegGuide, QuadrupedBackLeg
from rig_factory.objects.quadruped_objects.quadruped_bendy_back_leg import QuadrupedBendyBackLeg, QuadrupedBendyBackLegGuide



# Dynamic Objects

from rig_factory.objects.dynamic_parts.dynamics import DynamicsGuide, Dynamics
from rig_factory.objects.dynamic_parts.dynamic_fk_chain import DynamicFkChain, DynamicFkChainGuide
from rig_factory.objects.dynamic_parts.dynamic_fk_spline_chain import DynamicFkSplineChain, DynamicFkSplineChainGuide
from rig_factory.objects.dynamic_parts.dynamic_layered_ribbon_chain import DynamicLayeredRibbonChainGuide, DynamicLayeredRibbonChain

classes = dict()


def register_classes():
    update_classes(BaseNode)


def update_classes(base_class):
    classes[base_class.__name__] = base_class
    for sub_class in base_class.__subclasses__():
        update_classes(sub_class)
