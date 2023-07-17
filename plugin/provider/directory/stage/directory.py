from typing import Optional

from plugin.stage import Stage, StageContext


class CheckDirectory(Stage):
    def execute(self, context: StageContext) -> Optional[bool]:
        # FIXME To implement
        return True