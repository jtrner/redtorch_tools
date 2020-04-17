from biped import BipedGuide, Biped


class StandardBipedGuide(BipedGuide):

    def __init__(self, **kwargs):
        super(BipedGuide, self).__init__(**kwargs)
        self.toggle_class = Biped.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(StandardBipedGuide, cls).create(controller, **kwargs)

        return this

    def toggle_state(self):
        this = super(StandardBipedGuide, self).toggle_state()
        this.create_space_switcher(
            this.main.handles[0],
            this.spine.fk_handles[0],
            this.left_leg.ankle_handle
        )
        this.create_space_switcher(
            this.main.handles[0],
            this.spine.fk_handles[0],
            this.right_leg.ankle_handle
        )
        this.create_space_switcher(
            this.spine.fk_handles[3],
            this.left_arm.shoulder_handle,
            this.main.handles[0],
            this.spine.fk_handles[2],
            this.spine.fk_handles[1],
            this.spine.fk_handles[0],
            this.neck.fk_handles[-2],
            this.left_arm.wrist_handle
        )

        this.create_space_switcher(
            this.spine.fk_handles[3],
            this.left_arm.shoulder_handle,
            this.main.handles[0],
            this.left_arm.wrist_handle,
            this.spine.fk_handles[2],
            this.spine.fk_handles[1],
            this.spine.fk_handles[0],
            this.neck.fk_handles[-2],
            this.left_arm.elbow_handle
        )

        this.create_space_switcher(
            this.spine.fk_handles[3],
            this.right_arm.shoulder_handle,
            this.main.handles[0],
            this.spine.fk_handles[2],
            this.spine.fk_handles[1],
            this.spine.fk_handles[0],
            this.neck.fk_handles[-2],
            this.right_arm.wrist_handle
        )
        this.create_space_switcher(
            this.spine.fk_handles[3],
            this.right_arm.shoulder_handle,
            this.main.handles[0],
            this.right_arm.wrist_handle,
            this.spine.fk_handles[2],
            this.spine.fk_handles[1],
            this.spine.fk_handles[0],
            this.neck.fk_handles[-2],
            this.right_arm.elbow_handle
        )
        this.create_space_switcher(
            this.left_leg.ankle_handle,
            this.main.handles[0],
            this.spine.fk_handles[0],
            this.left_leg.knee_handle
        )
        this.create_space_switcher(
            this.right_leg.ankle_handle,
            this.main.handles[0],
            this.spine.fk_handles[0],
            this.right_leg.knee_handle
        )

        this.create_bind_skeleton()

        return this


class StandardBiped(Biped):

    def __init__(self, **kwargs):
        super(StandardBiped, self).__init__(**kwargs)
