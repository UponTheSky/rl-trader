from typing import Sequence, Mapping
from dataclasses import dataclass

import numpy as np

from ._interface import RLTradingModelInterface, State, Reward, Action


class BernTSState(State):
    _parameters: np.ndarray
    _index_to_action_id: dict[int, str]
    _action_id_to_index: dict[str, int]

    def __init__(
        self, *, parameters_with_action_ids: Mapping[str, Sequence[float]]
    ) -> None:
        self._parameters = np.array(
            list(parameters_with_action_ids.values()), dtype=float
        )
        action_ids = list(parameters_with_action_ids.keys())

        # i.i.d. beta distribution
        assert self._parameters.shape == (len(set(action_ids)), 2)
        print(self._parameters.shape, action_ids)

        self._index_to_action_id = dict(enumerate(action_ids))
        self._action_id_to_index = dict(
            (action, index) for index, action in enumerate(action_ids)
        )

    def get_max_action_id(self) -> str:
        """
        Sample from the current i.i.d. beta distribution, and select the action of
        the maximum probability density function value.
        """
        max_index = np.argmax(np.random.beta(self._parameters))
        return self._index_to_action_id[max_index]

    def set_parameter(self, *, action_id: str, reward: float) -> None:
        """
        Set a single element of the parameter vector, which is a 2-D numpy array.
        """
        index = self._action_id_to_index[action_id]
        self._parameters[index] += [reward, 1 - reward]

    @property
    def action_ids(self) -> set[str]:
        return set(self._action_id_to_index.keys())


@dataclass(frozen=True)
class BernTSAction(Action):
    """
    Args:
      - id: the identifier used internally in the platform.
      - key: the identifier used outside the platform for actual trading(e.g. Ticker)
    """

    id: str
    key: str


@dataclass(frozen=True)
class BernTSReward(Reward):
    """
    Args:
      - action_id: the id of the choosen action
      - reward: the reward value from having chosen the given action
    """

    action_id: str
    reward: float


class BernTSTradingModel(RLTradingModelInterface):
    """
    An implementation of Bernoulli Thompson Sampling algorithm.

    Reference: https://web.stanford.edu/~bvr/pubs/TS_Tutorial.pdf, Chapter 3.
    """

    _actions: set[BernTSAction]
    _state: BernTSState
    _mapper: dict[str, BernTSAction]

    def __init__(self, *, actions: set[BernTSAction], state: BernTSState) -> None:
        # check whether the actions are consistent with the state
        assert set(action.id for action in actions) == state.action_ids

        self._actions = actions
        self._state = state
        self._mapper = dict((action.id, action) for action in actions)

    def take_action(self) -> BernTSAction:
        max_action_id = self._state.get_max_action_id()
        return self._mapper[max_action_id]

    def earn_reward(self, *, reward: BernTSReward) -> None:
        self._state.set_parameter(action_id=reward.action_id, reward=reward.reward)

    @property
    def state(self) -> BernTSState:
        return self._state

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} - "
            "actions: {', '.join((action.key for action in self._actions))}"
        )

    def _log(self) -> str:
        raise NotImplementedError()
