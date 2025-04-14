from psychopy.visual import Circle, Rect, Polygon

class MIDStimuli:
    def __init__(self, window, config: dict):
        self.window = window
        radius = config.get('radius', 4)
        size = config.get('size', 8)
        cue_colors = config.get('cue_colors', {})
        target_color = config.get('target_color', 'black')

        # Cue shapes (with colors)
        self.cue_map = {
            'win': Circle(window, radius=radius, fillColor=cue_colors.get('win', 'magenta'), lineColor=None),
            'lose': Rect(window, width=size, height=size, fillColor=cue_colors.get('lose', 'yellow'), lineColor=None),
            'neut': Polygon(window, edges=3, size=size, fillColor=cue_colors.get('neut', 'cyan'), lineColor=None)
        }

        # Target shapes (all black)
        self.target_map = {
            'win': Circle(window, radius=radius, fillColor=target_color, lineColor=None),
            'lose': Rect(window, width=size, height=size, fillColor=target_color, lineColor=None),
            'neut': Polygon(window, edges=3, size=size, fillColor=target_color, lineColor=None)
        }

    def get_cue(self, condition): return self.cue_map[condition]
    def get_target(self, condition): return self.target_map[condition]



# # shape size params shared across conditions
# radius: 4
# size: 8

# # condition-specific fill colors
# cue_colors:
#   win: magenta
#   lose: yellow
#   neut: cyan

# target_color: black


# with open("mid_stimuli.yaml") as f:
#     stim_config = yaml.safe_load(f)

# stimuli = MIDStimuli(window, stim_config)
# cue_stim = stimuli.get_cue("win")
# target_stim = stimuli.get_target("win")