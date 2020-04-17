import rigging_widgets.animation_menu as amu
import maya.cmds as mc
from rig_factory.objects import *
import rigging_widgets.animation_menu.utilities.pose as pos
import rigging_widgets.animation_menu.utilities.selection as sel
import rig_factory.log as log


MENU_NAME = 'AnimationPartsMenu'


class MarkingMenu(object):

    def __init__(self):
        self._removeOld()
        self._build()

    def _build(self):

        mc.popupMenu(
            MENU_NAME, mm=1, b=2, aob=1, ctl=1, alt=0, sh=1, p="viewPanes", pmo=0,
            postMenuCommand=self._buildMarkingMenu
        )

    def _removeOld(self):

        if mc.popupMenu(MENU_NAME, ex=1):
            mc.deleteUI(MENU_NAME)

    def _buildMarkingMenu(self, menu, parent):

        mc.popupMenu(MENU_NAME, deleteAllItems=True, e=True)
        log.logger.info('MarkingMenu: building popup menu')
        if amu.shot_controller:
            log.logger.info('MarkingMenu: Found shot_controller')

            def expand_selection(*args):
                sel.expand_selection(amu.shot_controller)

            def expand_selection_recursive(*args):
                sel.expand_selection_recursive(amu.shot_controller)

            def mirror_pose_left(*args):
                pos.mirror_pose(
                    amu.shot_controller,
                    recursive=True,
                    source_side='right'

                )

            def mirror_pose_right(*args):
                pos.mirror_pose(
                    amu.shot_controller,
                    recursive=True,
                    source_side='left'
                )

            def flip_pose(*args):
                pos.flip_pose(
                    amu.shot_controller,
                    recursive=True
                )

            def copy_pose(*args):
                pos.copy_pose(
                    amu.shot_controller
                )

            def paste_pose(*args):
                pos.paste_pose(
                    amu.shot_controller
                )
            selection_menu = mc.menuItem(
                parent=menu,
                label="Selection",
                rp="S",
                subMenu=1
            )
            mc.menuItem(
                parent=selection_menu,
                label="Expand",
                rp="S",
                c=expand_selection
            )
            mc.menuItem(
                parent=selection_menu,
                label="Expand (recursive)",
                rp="SE",
                c=expand_selection_recursive
            )
            #pose_menu = mc.menuItem(
            #    parent=menu,
            #    label="Pose",
            #    rp="E",
            #    subMenu=1
            #)
            #mc.menuItem(
            #    parent=pose_menu,
            #    label="Copy Pose",
            #    rp="E",
            #    c=copy_pose
            #)
            #if pos.copied_pose_data:
            #    mc.menuItem(
            #        parent=pose_menu,
            #        label="Paste Pose",
            #        rp="NE",
            #        c=paste_pose
            #    )
            # mirror_menu = mc.menuItem(
            #     parent=menu,
            #     label="Mirror",
            #     rp="N",
            #     subMenu=1
            # )
            # mc.menuItem(
            #     parent=mirror_menu,
            #     label="Mirror Left",
            #     rp="NE",
            #     c=mirror_pose_left
            # )
            # mc.menuItem(
            #     parent=mirror_menu,
            #     label="Mirror Right",
            #     rp="NW",
            #     c=mirror_pose_right
            # )
            #
            # mc.menuItem(
            #     parent=mirror_menu,
            #     label="Flip",
            #     rp="N",
            #     c=flip_pose
            # )
            parts = amu.shot_controller.get_associated_parts(mc.ls(sl=True))
            if len(parts) > 1:
                mc.menuItem(
                    parent=menu,
                    label='Multiple Parts',
                    rp="W",
                    subMenu=1
                )
            elif len(parts) < 1:
                mc.menuItem(
                    parent=menu,
                    label='No Parts',
                    rp="W",
                    subMenu=1
                )
            else:
                part = parts[0]
                log.logger.info('MarkingMenu: found part : %s ' % part)

                part_menu = mc.menuItem(
                    parent=menu,
                    label=part.__class__.__name__.title(),
                    rp="W",
                    subMenu=1
                )
                if isinstance(part, (BipedLeg, BipedArm, BipedSpine, BipedNeck)):
                    log.logger.info('MarkingMenu: Part Can Toggle IK :  %s ' % part)

                    def toggle_ik(*args):
                        part.toggle_ik()

                    if part.settings_handle.plugs['ik_switch'].get_value() < 0.5:
                        mc.menuItem(
                            parent=part_menu,
                            label="Switch to IK",
                            rp="W",
                            c=toggle_ik
                        )
                    else:
                        mc.menuItem(
                            parent=part_menu,
                            label="Switch to FK",
                            rp="W",
                            c=toggle_ik
                        )
                if isinstance(part, Biped):
                    if not part.character_node:

                        def create_human_ik(*args):
                            part.create_human_ik()

                        def solve_t_pose(*args):
                            part.solve_t_pose()

                        mc.menuItem(
                            parent=part_menu,
                            label="Create Human IK",
                            rp="W",
                            c=create_human_ik
                        )
                        mc.menuItem(
                            parent=part_menu,
                            label="Solve T-Pose",
                            rp="W",
                            c=solve_t_pose
                        )


def rebuildMarkingMenu(*args):
    mc.evalDeferred("""MarkingMenu()""")