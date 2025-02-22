"""
Test cases for FiLM imputation model.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause


import os.path
import unittest

import numpy as np
import pytest

from pypots.imputation import FiLM
from pypots.optim import Adam
from pypots.utils.logging import logger
from pypots.nn.functional import calc_mse
from tests.global_test_config import (
    DATA,
    EPOCHS,
    DEVICE,
    TRAIN_SET,
    VAL_SET,
    TEST_SET,
    GENERAL_H5_TRAIN_SET_PATH,
    GENERAL_H5_VAL_SET_PATH,
    GENERAL_H5_TEST_SET_PATH,
    RESULT_SAVING_DIR_FOR_IMPUTATION,
    check_tb_and_model_checkpoints_existence,
)


class TestFiLM(unittest.TestCase):
    logger.info("Running tests for an imputation model FiLM...")

    # set the log and model saving path
    saving_path = os.path.join(RESULT_SAVING_DIR_FOR_IMPUTATION, "FiLM")
    model_save_name = "saved_film_model.pypots"

    # initialize an Adam optimizer
    optimizer = Adam(lr=0.001, weight_decay=1e-5)

    # initialize a FiLM model
    film = FiLM(
        DATA["n_steps"],
        DATA["n_features"],
        window_size=[2],
        multiscale=[1, 2],
        modes1=512,
        dropout=0.5,
        d_model=512,
        epochs=EPOCHS,
        saving_path=saving_path,
        optimizer=optimizer,
        device=DEVICE,
    )

    @pytest.mark.xdist_group(name="imputation-film")
    def test_0_fit(self):
        self.film.fit(TRAIN_SET, VAL_SET)

    @pytest.mark.xdist_group(name="imputation-film")
    def test_1_impute(self):
        imputation_results = self.film.predict(TEST_SET)
        assert not np.isnan(
            imputation_results["imputation"]
        ).any(), "Output still has missing values after running impute()."

        test_MSE = calc_mse(
            imputation_results["imputation"],
            DATA["test_X_ori"],
            DATA["test_X_indicating_mask"],
        )
        logger.info(f"FiLM test_MSE: {test_MSE}")

    @pytest.mark.xdist_group(name="imputation-film")
    def test_2_parameters(self):
        assert hasattr(self.film, "model") and self.film.model is not None

        assert hasattr(self.film, "optimizer") and self.film.optimizer is not None

        assert hasattr(self.film, "best_loss")
        self.assertNotEqual(self.film.best_loss, float("inf"))

        assert hasattr(self.film, "best_model_dict") and self.film.best_model_dict is not None

    @pytest.mark.xdist_group(name="imputation-film")
    def test_3_saving_path(self):
        # whether the root saving dir exists, which should be created by save_log_into_tb_file
        assert os.path.exists(self.saving_path), f"file {self.saving_path} does not exist"

        # check if the tensorboard file and model checkpoints exist
        check_tb_and_model_checkpoints_existence(self.film)

        # save the trained model into file, and check if the path exists
        saved_model_path = os.path.join(self.saving_path, self.model_save_name)
        self.film.save(saved_model_path)

        # test loading the saved model, not necessary, but need to test
        self.film.load(saved_model_path)

    @pytest.mark.xdist_group(name="imputation-film")
    def test_4_lazy_loading(self):
        self.film.fit(GENERAL_H5_TRAIN_SET_PATH, GENERAL_H5_VAL_SET_PATH)
        imputation_results = self.film.predict(GENERAL_H5_TEST_SET_PATH)
        assert not np.isnan(
            imputation_results["imputation"]
        ).any(), "Output still has missing values after running impute()."

        test_MSE = calc_mse(
            imputation_results["imputation"],
            DATA["test_X_ori"],
            DATA["test_X_indicating_mask"],
        )
        logger.info(f"Lazy-loading FiLM test_MSE: {test_MSE}")


if __name__ == "__main__":
    unittest.main()
