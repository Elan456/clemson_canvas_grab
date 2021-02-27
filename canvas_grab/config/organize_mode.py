import questionary
from canvas_grab.configurable import Configurable
from canvas_grab.utils import find_choice
from canvas_grab.snapshot import CanvasFileSnapshot, CanvasModuleSnapshot
from canvas_grab.error import CanvasGrabCliError


class OrganizeMode(Configurable):

    def __init__(self):
        self.mode = 'module'
        self.delete_file = False

    def get_snapshots(self, course):
        if self.mode == 'module_link':
            canvas_snapshot_module = CanvasModuleSnapshot(
                course, True)
        else:
            canvas_snapshot_module = CanvasModuleSnapshot(
                course)
        canvas_snapshot_file = CanvasFileSnapshot(course)

        if self.mode == 'module' or self.mode == 'module_link':
            canvas_snapshots = [canvas_snapshot_module, canvas_snapshot_file]
        elif self.mode == 'file':
            canvas_snapshots = [canvas_snapshot_file, canvas_snapshot_module]
        else:
            raise CanvasGrabCliError(f"Unsupported organize mode {mode}")

        return canvas_snapshots

    def to_config(self):
        return {
            'mode': self.mode,
            'delete_file': self.delete_file
        }

    def from_config(self, config):
        self.mode = config['mode']
        self.delete_file = config['delete_file']

    def interact(self):
        choices = [
            questionary.Choice('By module (recommended)', 'module'),
            questionary.Choice(
                'By module with pages and links', 'module_link'),
            questionary.Choice('As-is in file list', 'file'),
            questionary.Choice('Custom', 'custom',
                               disabled='not supported yet')
        ]
        self.mode = questionary.select(
            'Select default file organization mode',
            choices,
            default=find_choice(choices, self.mode)
        ).unsafe_ask()
        choices = [
            questionary.Choice(
                "Delete local files if they disappears on Canvas", True),
            questionary.Choice("Always keep local files", False)
        ]
        self.delete_file = questionary.select(
            'How to handle deleted files on Canvas',
            choices,
            default=find_choice(choices, self.delete_file)
        ).unsafe_ask()
