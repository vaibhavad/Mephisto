#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Dict, Optional, Any, TYPE_CHECKING
from mephisto.server.blueprints.static_task.static_agent_state import StaticAgentState
import os
import json

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet


DATA_FILE = "agent_data.json"


class AcuteEvalAgentState(StaticAgentState):
    """
    Agent state for acute eval tasks - equivalent to StaticAgentState but 
    doesn't have file IO
    """

    def update_data(self, packet: "Packet") -> None:
        """
        Process the incoming data packet, and handle
        updating the state
        """
        assert (
            packet.data.get("MEPHISTO_is_submit") is True
        ), "Static tasks should only have final act"
        self.state["outputs"] = packet.data["task_data"]
        self.save_data()
