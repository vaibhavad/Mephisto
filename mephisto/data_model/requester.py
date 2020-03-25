#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.core.utils import get_crowd_provider_from_type

from typing import List, Optional, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup


class Requester(ABC):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        self.db_id: str = db_id
        self.db: "MephistoDB" = db
        row = db.get_requester(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.provider_type: str = row["provider_type"]
        self.requester_name: str = row["requester_name"]

    def __new__(cls, db: "MephistoDB", db_id: str) -> "Requester":
        """
        The new method is overridden to be able to automatically generate
        the expected Requester class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Requester
        as you will instead be returned the correct Requester class according to
        the crowdprovider associated with this Requester.
        """
        if cls == Requester:
            # We are trying to construct a Requester, find what type to use and
            # create that instead
            row = db.get_requester(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).RequesterClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def __str__(self):
        return f"{self.requester_name}@{self.provider_type}"
        
    def get_task_runs(self) -> List["TaskRun"]:
        """
        Return the list of task runs that are run by this requester
        """
        return self.db.find_task_runs(requester_id=self.db_id)

    def get_total_spend(self) -> float:
        """
        Return the total amount of funding spent by this requester
        across all tasks.
        """
        task_runs = self.db.find_task_runs(requester_id=self.db_id)
        total_spend = 0.0
        for run in task_runs:
            total_spend += run.get_total_spend()
        return total_spend

    def is_sandbox(self) -> bool:
        """
        Determine if this is a requester on a sandbox/test account
        """
        return False

    @staticmethod
    def _register_requester(
        db: "MephistoDB", requester_id: str, provider_type: str
    ) -> "Requester":
        """
        Create an entry for this requester in the database
        """
        db_id = db.new_requester(requester_id, provider_type)
        return Requester(db, db_id)

    # Children classes should implement the following methods

    def register(self, args: Optional[Dict[str, str]] = None) -> None:
        """
        Register this requester with the crowd provider by providing any required credentials
        or such. If no args are provided, assume the registration is already made and try
        to assert it as such.

        Should throw an exception if something is wrong with provided registration arguments.
        """
        raise NotImplementedError()

    def is_registered(self) -> bool:
        """Check to see if this requester has already been registered"""
        raise NotImplementedError()

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Add the arguments to register this requester to the crowd provider,
        the group's 'description' attribute should be used for any high level
        help on how to get the details.

        The `name` argument is required.

        If the description field is left empty, the argument group is ignored
        """
        # group.description = 'For `Requester`, Retrieve the following at xyz'
        # group.add_argument('--username', help='Login username for requester')
        # group.add_argument('--secret-key', help='Secret key found...')
        group.add_argument("--name", help="Identifier for MephistoDB")
        return

    def get_available_budget(self) -> float:
        """
        Return the funds that this requester profile has available for usage with
        its crowdsourcing vendor
        """
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        """
        Produce a dict of this requester and important features for json serialization
        """
        return {
            "requester_id": self.db_id,
            "provider_type": self.provider_type,
            "requester_name": self.requester_name,
            "registered": self.is_registered(),
        }

    # TODO add a way to manage creation and validation of qualifications
    # for a given requester?
    # TODO add qualifications to the data model

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        """
        Try to create a new requester by this name, raise an exception if
        the name already exists.

        Implementation should call _register_requester(db, requester_id) when sure the requester
        can be successfully created to have it put into the db and return the result.
        """
        raise NotImplementedError()
