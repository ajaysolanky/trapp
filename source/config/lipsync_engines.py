from enum import Enum
from video_lipsync import VideoLipsyncGooey, VideoLipsyncSynchronicity, SimpleOverlay

# value should be and ISO-639-1 language code
class LipsyncEngines(Enum):
    GOOEY = VideoLipsyncGooey
    SYNCHRONICITY = VideoLipsyncSynchronicity
    SIMPLE_OVERLAY = SimpleOverlay
    # REPLICATE = VideoLipsyncReplicate