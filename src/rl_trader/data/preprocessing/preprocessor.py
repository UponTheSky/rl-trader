from typing import Literal, Any
import logging

import pandas as pd

from rl_trader.common.exceptions import ValidationError
from ._interface import DataPreprocessorInterface


class DataPreprocessor(DataPreprocessorInterface):
    _logger: logging.Logger  # TODO: replace with the custom logger

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def rearrange_raw_data(
        *, self, input: pd.DataFrame, data_schema: pd.Index
    ) -> pd.DataFrame:
        try:
            if not data_schema.difference(input.columns).empty:
                raise ValidationError(
                    "There are missing fields in the returned dataframe "
                    "compared to the provided schema"
                )

            input.drop(columns=input.columns.difference(data_schema), inplace=True)
        except Exception as error:
            self._log(message=str(error))
            raise

    def handle_missing_values(
        *,
        self,
        input: pd.DataFrame,
        option: Literal["exclude", "replace"],
        replace_value: Any,
    ) -> pd.DataFrame:
        ...

    def _log(self, *, message: str, level: str) -> None:
        # TODO: use the custom logger
        return self._logger.info(message)

    def __repr__(self) -> str:
        return f"Compent '{self.__class__.__name__}'"
