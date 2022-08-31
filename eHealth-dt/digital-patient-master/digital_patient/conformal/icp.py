#!/usr/bin/env python

# Authors: Maharin Afroj

from __future__ import division
from collections import defaultdict
from functools import partial

import numpy as np
from sklearn.base import BaseEstimator

from .base import RegressorMixin, ClassifierMixin
from .util import calc_p

class BaseIcp(BaseEstimator):
	def __init__(self, nc_function, condition=None):
		self.cal_x, self.cal_y = None, None
		self.nc_function = nc_function

	
		default_condition = lambda x: 0
		is_default = (callable(condition) and
		              (condition.__code__.co_code ==
		               default_condition.__code__.co_code))

		if is_default:
			self.condition = condition
			self.conditional = False
		elif callable(condition):
			self.condition = condition
			self.conditional = True
		else:
			self.condition = lambda x: 0
			self.conditional = False

	def fit(self, x, y):
		
		# TODO: incremental?
		self.nc_function.fit(x, y)

	def calibrate(self, x, y, increment=False):
		
		self._calibrate_hook(x, y, increment)
		self._update_calibration_set(x, y, increment)

		if self.conditional:
			category_map = np.array([self.condition((x[i, :], y[i]))
									 for i in range(y.size)])
			self.categories = np.unique(category_map)
			self.cal_scores = defaultdict(partial(np.ndarray, 0))

			for cond in self.categories:
				idx = category_map == cond
				cal_scores = self.nc_function.score(self.cal_x[idx, :],
				                                    self.cal_y[idx])
				self.cal_scores[cond] = np.sort(cal_scores)[::-1]
		else:
			self.categories = np.array([0])
			cal_scores = self.nc_function.score(self.cal_x, self.cal_y)
			# self.cal_scores = {0: np.sort(cal_scores)[::-1]}
			self.cal_scores = {0: cal_scores}

	def _calibrate_hook(self, x, y, increment):
		pass

	def _update_calibration_set(self, x, y, increment):
		if increment and self.cal_x is not None and self.cal_y is not None:
			self.cal_x = np.vstack([self.cal_x, x])
			self.cal_y = np.hstack([self.cal_y, y])
		else:
			self.cal_x, self.cal_y = x, y

class IcpClassifier(BaseIcp, ClassifierMixin):
	
	def __init__(self, nc_function, condition=None, smoothing=True):
		super(IcpClassifier, self).__init__(nc_function, condition)
		self.classes = None
		self.smoothing = smoothing

	def _calibrate_hook(self, x, y, increment=False):
		self._update_classes(y, increment)

	def _update_classes(self, y, increment):
		if self.classes is None or not increment:
			self.classes = np.unique(y)
		else:
			self.classes = np.unique(np.hstack([self.classes, y]))

	def predict(self, x, significance=None):
		

		n_test_objects = x.shape[0]
		p = np.zeros((n_test_objects, self.classes.size))

		ncal_ngt_neq = self._get_stats(x)

		for i in range(len(self.classes)):
			for j in range(n_test_objects):
				p[j, i] = calc_p(ncal_ngt_neq[j, i, 0],
				                 ncal_ngt_neq[j, i, 1],
				                 ncal_ngt_neq[j, i, 2],
				                 self.smoothing)

		if significance is not None:
			return p > significance
		else:
			return p

	def _get_stats(self, x):
		n_test_objects = x.shape[0]
		ncal_ngt_neq = np.zeros((n_test_objects, self.classes.size, 3))
		for i, c in enumerate(self.classes):
			test_class = np.zeros(x.shape[0], dtype=self.classes.dtype)
			test_class.fill(c)

			test_nc_scores = self.nc_function.score(x, test_class)
			for j, nc in enumerate(test_nc_scores):
				cal_scores = self.cal_scores[self.condition((x[j, :], c))][::-1]
				n_cal = cal_scores.size

				idx_left = np.searchsorted(cal_scores, nc, 'left')
				idx_right = np.searchsorted(cal_scores, nc, 'right')

				ncal_ngt_neq[j, i, 0] = n_cal
				ncal_ngt_neq[j, i, 1] = n_cal - idx_right
				ncal_ngt_neq[j, i, 2] = idx_right - idx_left

		return ncal_ngt_neq

	def predict_conf(self, x):
		
		p = self.predict(x, significance=None)
		label = p.argmax(axis=1)
		credibility = p.max(axis=1)
		for i, idx in enumerate(label):
			p[i, idx] = -np.inf
		confidence = 1 - p.max(axis=1)

		return np.array([label, confidence, credibility]).T

class IcpRegressor(BaseIcp, RegressorMixin):

	def __init__(self, nc_function, condition=None):
		super(IcpRegressor, self).__init__(nc_function, condition)

	def predict(self, x, significance=None):
	
		# TODO: interpolated p-values

		n_significance = (99 if significance is None
		                  else np.array(significance).size)

		if n_significance > 1:
			prediction = np.zeros((x.shape[0], x.shape[1], x.shape[2], 2, n_significance))
		else:
			prediction = np.zeros((x.shape[0], 2))

		condition_map = np.zeros(x.shape)

		for condition in self.categories:
			idx = condition_map == condition
			if np.sum(idx) > 0:
				p = self.nc_function.predict(x,
				                             self.cal_scores[condition],
			
				prediction = p

		return prediction


class OobCpClassifier(IcpClassifier):
	def __init__(self,
	             nc_function,
	             condition=None,
	             smoothing=True):
		super(OobCpClassifier, self).__init__(nc_function,
		                                      condition,
		                                      smoothing)

	def fit(self, x, y):
		super(OobCpClassifier, self).fit(x, y)
		super(OobCpClassifier, self).calibrate(x, y, False)

	def calibrate(self, x, y, increment=False):
	
		pass


class OobCpRegressor(IcpRegressor):
	def __init__(self,
				 nc_function,
				 condition=None):
		super(OobCpRegressor, self).__init__(nc_function,
											  condition)

	def fit(self, x, y):
		super(OobCpRegressor, self).fit(x, y)
		super(OobCpRegressor, self).calibrate(x, y, False)

	def calibrate(self, x, y, increment=False):
		
		pass
