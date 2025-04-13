from psychopy import visual
from psychopy.hardware import keyboard
from psychopy.visual import Circle, Rect, Polygon
from types import SimpleNamespace
from datetime import datetime
from psyflow.seedcontrol import setup_seed_for_settings


def exp_setup(subdata):
    """
    Initializes window, stimuli, experiment settings, and keyboard.

    Args:
        subdata (list): Subject info including ID.
    Returns:
        win (visual.Window): The PsychoPy window object.
        kb (keyboard.Keyboard): Keyboard input handler.
        settings (SimpleNamespace): Experimental settings and stimuli.
    """
    win = visual.Window(
        size=[1920, 1080],
        monitor="testMonitor",
        units="deg",
        screen=1,
        color="white",
        fullscr=False,
        gammaErrorPolicy='ignore'  # avoid gamma ramp errors
    )

    # Define settings
    settings = SimpleNamespace()
    settings.TotalBlocks = 2
    settings.TotalTrials = 20
    settings.TrialsPerBlock = settings.TotalTrials // settings.TotalBlocks

    # random seed
    settings = setup_seed_for_settings(settings, subdata, mode="indiv") # each sub will have a unique seed

    # Cue stimuli (colored)
    settings.CircleCue = Circle(win, radius=4, fillColor='magenta', lineColor=None) # Reward cue (based on image)
    settings.SquareCue = Rect(win, width=8, height=8, fillColor='yellow', lineColor=None) # Punishment cue (based on image)
    settings.TriangleCue = Polygon(win, edges=3, size=8, fillColor='cyan', lineColor=None) # Neutral cue (based on image)

    # Target stimulus (black)
    settings.CircleProb = Circle(win, radius=4, fillColor='black', lineColor=None)
    settings.SquareProb = Rect(win, width=8, height=8, fillColor='black', lineColor=None)
    settings.TriangleProb = Polygon(win, edges=3, size=8, fillColor='black', lineColor=None)


    # # Cue stimuli (using images)
    # settings.WinCue = ImageStim(win, image=os.path.join(img_path, 'WinCue.BMP'), size=(8, 8)) # Example size, adjust as needed
    # settings.LoseCue = ImageStim(win, image=os.path.join(img_path, 'LoseCue.BMP'), size=(8, 8)) # Example size, adjust as needed
    # settings.NeutralCue = ImageStim(win, image=os.path.join(img_path, 'NeutralCue.BMP'), size=(8, 8)) # Example size, adjust as needed

    # # Target stimulus (using image)
    # settings.WinProbe = ImageStim(win, image=os.path.join(img_path, 'WinProbe.BMP'), size=(8, 8)) # Example size, adjust as needed
    # settings.LoseProbe = ImageStim(win, image=os.path.join(img_path, 'LoseProbe.BMP'), size=(8, 8)) # Example size, adjust as needed
    # settings.NeutralProbe = ImageStim(win, image=os.path.join(img_path, 'NeutralProbe.BMP'), size=(8, 8)) # Example size, adjust as needed

    settings.cueTypes = ['win', 'lose', 'neut']  # Representing the cue conditions
    # Timing
    settings.fixDuration = 0.5
    settings.cueDuration = 0.5
    settings.antiDuration = 0.5
    settings.ProbDuration = 0.5 # Example duration, adjust as needed
    settings.fbDuration = 1
    settings.iti=1

    # Keyboard settings
    settings.responseKey = 'space' # Assuming a single key press to the target
    settings.keyList = [settings.responseKey]

    # File naming
    dt_string = datetime.now().strftime("%H%M%d%m")
    settings.outfile = f"Subject{subdata[0]}_{dt_string}.csv"

    kb = keyboard.Keyboard()

    return win, kb, settings