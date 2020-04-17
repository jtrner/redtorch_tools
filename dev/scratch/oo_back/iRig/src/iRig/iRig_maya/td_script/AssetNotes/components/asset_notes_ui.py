from AssetNotes.components import api_layer
reload(api_layer)

class AssetNotesUI(api_layer.AssetNotesAPILayer):
    def __init__(self):
        super(AssetNotesUI, self).__init__()
        self.episode_dropdown_setup()
        self.asset_list_setup()
