"""
The implementation of LOCF (Last Observed Carried Forward) for the partially-observed time-series imputation task.

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import warnings
from typing import Union, Optional

import h5py
import numpy as np
import torch

from .core import locf_numpy, locf_torch
from ..base import BaseImputer


class LOCF(BaseImputer):
    """LOCF (Last Observed Carried Forward) imputation method. A naive imputation method that fills missing values
    with the last observed value. When time-series data gets inverse on the time dimension, this method can also be
    seen as NOCB (Next Observation Carried Backward). Simple but commonly used in practice.

    Parameters
    ----------
    first_step_imputation : str, default='backward'
        With LOCF, the observed values are carried forward to impute the missing ones. But if the first value
        is missing, there is no value to carry forward. This parameter is used to determine the strategy to
        impute the missing values at the beginning of the time-series sequence after LOCF is applied.
        It can be one of ['backward', 'zero', 'median', 'nan'].
        If 'nan', the missing values at the sequence beginning will be left as NaNs.
        If 'zero', the missing values at the sequence beginning will be imputed with 0.
        If 'backward', the missing values at the beginning of the time-series sequence will be imputed with the
        first observed value in the sequence, i.e. the first observed value will be carried backward to impute
        the missing values at the beginning of the sequence. This method is also known as NOCB (Next Observation
        Carried Backward). If 'median', the missing values at the sequence beginning will be imputed with the overall
        median values of features in the dataset.
        If `first_step_imputation` is not "nan", if missing values still exist (this is usually caused by whole feature
        missing) after applying `first_step_imputation`, they will be filled with 0.

    """

    def __init__(
        self,
        first_step_imputation: str = "zero",
        device: Optional[Union[str, torch.device, list]] = None,
    ):
        super().__init__(device=device)
        assert first_step_imputation in ["nan", "zero", "backward", "median"]
        self.first_step_imputation = first_step_imputation

    def fit(
        self,
        train_set: Union[dict, str],
        val_set: Optional[Union[dict, str]] = None,
        file_type: str = "hdf5",
    ) -> None:
        """Train the imputer on the given data.

        Warnings
        --------
        LOCF does not need to run fit().
        Please run func ``predict()`` directly.

        """
        warnings.warn(
            "LOCF (Last Observed Carried Forward) imputation class has no parameter to train. "
            "Please run func `predict()` directly."
        )

    def predict(
        self,
        test_set: Union[dict, str],
        file_type: str = "hdf5",
    ) -> dict:
        """Make predictions for the input data with the trained model.

        Parameters
        ----------
        test_set : dict or str
            The dataset for model validating, should be a dictionary including keys as 'X',
            or a path string locating a data file supported by PyPOTS (e.g. h5 file).
            If it is a dict, X should be array-like of shape [n_samples, sequence length (n_steps), n_features],
            which is time-series data for validating, can contain missing values, and y should be array-like of shape
            [n_samples], which is classification labels of X.
            If it is a path string, the path should point to a data file, e.g. a h5 file, which contains
            key-value pairs like a dict, and it has to include keys as 'X' and 'y'.

        file_type :
            The type of the given file if test_set is a path string.

        Returns
        -------
        result_dict: dict
            Prediction results in a Python Dictionary for the given samples.
            It should be a dictionary including keys as 'imputation', 'classification', 'clustering', and 'forecasting'.
            For sure, only the keys that relevant tasks are supported by the model will be returned.
        """
        if isinstance(test_set, str):
            with h5py.File(test_set, "r") as f:
                X = f["X"][:]
        else:
            X = test_set["X"]

        assert len(X.shape) == 3, (
            f"Input X should have 3 dimensions [n_samples, n_steps, n_features], "
            f"but the actual shape of X: {X.shape}"
        )
        if isinstance(X, list):
            X = np.asarray(X)

        if isinstance(X, np.ndarray):
            imputed_data = locf_numpy(X, self.first_step_imputation)
        elif isinstance(X, torch.Tensor):
            imputed_data = locf_torch(X, self.first_step_imputation)
        else:
            raise TypeError("X must be type of list/np.ndarray/torch.Tensor, " f"but got {type(X)}")

        result_dict = {
            "imputation": imputed_data,
        }
        return result_dict

    def impute(
        self,
        test_set: Union[dict, str],
        file_type: str = "hdf5",
    ) -> np.ndarray:
        """Impute missing values in the given data with the trained model.

        Parameters
        ----------
        test_set :
            The data samples for testing, should be array-like of shape [n_samples, sequence length (n_steps),
            n_features], or a path string locating a data file, e.g. h5 file.

        file_type :
            The type of the given file if X is a path string.

        Returns
        -------
        array-like, shape [n_samples, sequence length (n_steps), n_features],
            Imputed data.
        """

        result_dict = self.predict(test_set, file_type=file_type)
        return result_dict["imputation"]
