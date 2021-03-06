#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
　このテストファイルでは実装された自動微分により得られた勾配と
数値微分により得られた勾配を比較し、一致しているかどうかを
確認する。

　テスト時は計算精度をfloat64として実行する必要がある。
そのため、現在(2017/5/8)ではCPUにおける計算のみを
テストしている。
"""
from __future__ import division, print_function

import pytest

import numpy as np
from renom.config import precision
import renom as rm
from renom.core import Variable
from renom.operation import sum
from renom.layers.activation.sigmoid import sigmoid
from renom.layers.activation.tanh import tanh
from renom.layers.activation.relu import relu

from renom.layers.function.dense import Dense
from renom.layers.function.conv2d import Conv2d
from renom.layers.function.deconv2d import Deconv2d
from renom.layers.function.pool2d import MaxPool2d, AveragePool2d
from renom.layers.function.dropout import Dropout, SpatialDropout
from renom.layers.function.lstm import Lstm
from renom.layers.function.batch_normalize import BatchNormalize,\
    BATCH_NORMALIZE_FEATUREMAP
from renom.layers.function.lrn import Lrn
from test_utility import auto_diff, numeric_diff

from renom.cuda import is_cuda_active, set_cuda_active, curand_generator
from test_utility import skipgpu

if precision is not np.float64:
    pytestmark = pytest.mark.skip()


def rand(shape):
    return np.array(np.random.rand(*shape), dtype=np.float64)


def randInteger(shape):
    return np.array(np.random.randint(0, 2, shape), dtype=np.float64)


def onehot(shape):
    N = shape[0]
    D = shape[1]
    ret = np.zeros(shape, dtype=np.float64)
    if D > 1:
        for n in range(N):
            r = np.random.randint(0, D)
            ret[n, r] = 1.
    else:
        ret[np.random.randint(0, N)] = 1
    return ret


def compare(func, node, *args):
    ad = auto_diff(func, node, *args)
    nd = numeric_diff(func, node, *args)
    print("ad = \n{}".format(ad))
    print("nd = \n{}".format(nd))
    print("difference = \n{}".format(ad - nd))
    assert np.allclose(ad, nd, atol=1e-5, rtol=1e-3)


@pytest.mark.parametrize("node, x, raise_error", [
    [Variable(rand((2, 2))), rand((2, 2)), False],
    [Variable(rand((2, 2, 2, 2))), rand((2, 2, 2, 2)), False],
    [Variable(rand((2, 1))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2, 1)), True],
    [Variable(rand((2,))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2,)), True],
])
def test_add(node, x, raise_error, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    # Add
    def func_add1(node, x):
        return sum(x + node)
    compare(func_add1, node, node, x)

    def func_add2(node, x):
        return sum(node + x)
    compare(func_add2, node, node, x)

    def func_iadd1(node, x):
        node += x
        return sum(node)
    try:
        # An assertion error occur when shape mismatching.
        compare(func_iadd1, node, node, x)
        assert not raise_error
    except:
        assert raise_error

    def func_iadd2(node, x):
        x += node
        return sum(node)
    try:
        # An assertion error occur when shape mismatching.
        compare(func_iadd2, node, node, x)
        assert not raise_error
    except:
        assert raise_error


@pytest.mark.parametrize("node, x, raise_error", [
    [Variable(rand((2, 2))), rand((2, 2)), False],
    [Variable(rand((2, 2, 2, 2))), rand((2, 2, 2, 2)), False],
    [Variable(rand((2, 1))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2, 1)), True],
    [Variable(rand((2,))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2,)), True],
])
def test_sub(node, x, raise_error, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func_sub1(node, x):
        return sum(x - node)
    compare(func_sub1, node, node, x)

    def func_sub2(node, x):
        return sum(node - x)
    compare(func_sub2, node, node, x)

    def func_isub1(node, x):
        node -= x
        return sum(node)
    try:
        compare(func_isub1, node, node, x)
        assert not raise_error
    except:
        assert raise_error

    def func_isub2(node, x):
        x -= node
        return sum(node)
    try:
        compare(func_isub2, node, node, x)
        assert not raise_error
    except:
        assert raise_error


@pytest.mark.parametrize("node, x, raise_error", [
    [Variable(rand((2, 2))), rand((2, 2)), False],
    [Variable(rand((2, 2, 2, 2))), rand((2, 2, 2, 2)), False],
    [Variable(rand((2, 1))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2, 1)), True],
    [Variable(rand((2,))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2,)), True],
])
def test_mul(node, x, raise_error, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func_mul1(node, x):
        return sum(x * node)
    compare(func_mul1, node, node, x)

    def func_mul2(node, x):
        return sum(node * x)
    compare(func_mul2, node, node, x)

    def func_imul1(node, x):
        node *= x
        return sum(node)
    try:
        compare(func_imul1, node, node, x)
        assert not raise_error
    except:
        assert raise_error

    def func_imul2(node, x):
        x *= node
        return sum(node)
    try:
        compare(func_imul2, node, node, x)
        assert not raise_error
    except:
        assert raise_error


@pytest.mark.parametrize("node, x, raise_error", [
    [Variable(rand((2, 2))), rand((2, 2)), False],
    [Variable(rand((2, 2, 2, 2))), rand((2, 2, 2, 2)), False],
    [Variable(rand((2, 1))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2, 1)), True],
    [Variable(rand((2,))), rand((2, 2)), True],
    [Variable(rand((2, 2))), rand((2,)), True],
])
def test_div(node, x, raise_error, use_gpu):
    node = Variable(node)
    x = np.array(x)
    set_cuda_active(use_gpu)

    def func_div1(node, x):
        return sum(x / node)
    compare(func_div1, node, node, x)

    def func_div2(node, x):
        return sum(node / x)
    compare(func_div2, node, node, x)

    def func_idiv1(node, x):
        node /= x
        return sum(node)
    try:
        compare(func_idiv1, node, node, x)
        assert not raise_error
    except:
        assert raise_error

    def func_idiv2(node, x):
        x /= node
        return sum(node)
    try:
        compare(func_idiv2, node, node, x)
        assert not raise_error
    except:
        assert raise_error


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
])
def test_tanh_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(tanh(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
    Variable(rand((2, 2, 2, 2))),
])
def test_sigmoid_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(sigmoid(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
    Variable(rand((2, 2, 2, 2))),
])
def test_relu_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(relu(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
    Variable(rand((2, 2, 2, 2))),
])
def test_selu_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.selu(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
    Variable(rand((2, 2, 2, 2))),
])
def test_elu_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.elu(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((2,))),
    Variable(rand((2, 2, 2, 2))),
])
def test_leaky_relu_activation(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.leaky_relu(node))
    compare(func, node, node)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((2, 2))), onehot((2, 2))],
    [Variable(rand((2, 3))), onehot((2, 3))],
    [Variable(rand((1, 2))), onehot((1, 2))],
    [Variable(rand((2, 2, 3, 3))), onehot((2, 2, 3, 3))],
])
def test_softmax(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return rm.cross_entropy(rm.softmax(node), x)
    compare(func, node, node, x)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1, 2))),
])
def test_dense(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = Dense(output_size=2)

    def func(node):
        return sum(layer(node))
    compare(func, node, node)
    compare(func, layer.params["w"], node)
    compare(func, layer.params["b"], node)


@pytest.mark.parametrize("node", [
    np.array([[0, ], [1, ]]),
    np.array([[0, ], [1, ], [0, ]]),
])
def test_embedding(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = rm.Embedding(output_size=2, input_size=2)

    def func(node):
        return sum(layer(node))
    compare(func, layer.params["w"], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 1))),
    Variable(rand((2, 2))),
    Variable(rand((20, 2))),
])
def test_batch_normalize(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = BatchNormalize()

    def func(node):
        return sum(layer(node))
    compare(func, node, node)
    compare(func, layer.params["w"], node)
    compare(func, layer.params["b"], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_lrn(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = Lrn()

    def func(node):
        return sum(layer(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_batch_normalize_featurewise(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = BatchNormalize(mode=BATCH_NORMALIZE_FEATUREMAP)

    def func(node):
        return sum(layer(node))
    compare(func, node, node)
    compare(func, layer.params["w"], node)
    compare(func, layer.params["b"], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_conv2d(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = Conv2d(channel=3)

    def func(node):
        return sum(layer(node))
    compare(func, node, node)
    compare(func, layer.params["w"], node)
    compare(func, layer.params["b"], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 3, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_deconv2d(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = Deconv2d(channel=3)

    def func(node):
        return sum(layer(node))
    compare(func, node, node)
    compare(func, layer.params["w"], node)
    compare(func, layer.params["b"], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 3, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_max_pool2d(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = MaxPool2d()

    def func(node):
        return sum(layer(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 3, 3, 3))),
    Variable(rand((2, 3, 4, 5))),
])
def test_average_pool2d(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = AveragePool2d()

    def func(node):
        return sum(layer(node))
    compare(func, node, node)


@pytest.mark.parametrize("node, seed", [
    [Variable(rand((2, 2))), 1],
    [Variable(rand((2, 5))), 2],
])
def test_dropout(node, seed, use_gpu):
    use_gpu = use_gpu and is_cuda_active()
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = Dropout()

    def func(node):
        if use_gpu:
            curand_generator().set_seed(seed)
        else:
            np.random.seed(seed)
        return sum(layer(node))
    compare(func, node, node)


@pytest.mark.parametrize("node, seed", [
    [Variable(rand((2, 2, 2, 2))), 1],
    [Variable(rand((2, 5, 1, 1))), 2],
    [Variable(rand((2, 2, 3, 3))), 3]
])
def test_spatial_dropout(node, seed, use_gpu):
    use_gpu = use_gpu and is_cuda_active()
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer = SpatialDropout()

    def func(node):
        if use_gpu:
            curand_generator().set_seed(seed)
        else:
            np.random.seed(seed)
        return sum(layer(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1, 2))),
])
def test_lstm(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer1 = Lstm(output_size=4)

    def func(node):
        loss = 0
        for _ in range(3):
            loss += sum(layer1(node))
        layer1.truncate()
        return loss

    compare(func, node, node)
    for k in layer1.params.keys():
        compare(func, layer1.params[k], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1, 2))),
])
def test_lstm_temporal_connection(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer1 = Lstm(output_size=4)

    def func(node):
        loss = 0
        for _ in range(3):
            loss = sum(layer1(node))
        layer1.truncate()
        return loss

    compare(func, node, node)
    for k in layer1.params.keys():
        compare(func, layer1.params[k], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1, 2))),
])
def test_peepholelstm(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer1 = rm.PeepholeLstm(output_size=4)

    def func(node):
        loss = 0
        for _ in range(3):
            loss += sum(layer1(node))
        layer1.truncate()
        return loss

    compare(func, node, node)
    for k in layer1.params.keys():
        compare(func, layer1.params[k], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1, 2))),
])
def test_peepholelstm_temporal_connection(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    layer1 = rm.PeepholeLstm(output_size=4)

    def func(node):
        loss = 0
        for _ in range(3):
            loss = sum(layer1(node))
        layer1.truncate()
        return loss

    compare(func, node, node)
    for k in layer1.params.keys():
        compare(func, layer1.params[k], node)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((2, 2))), onehot((2, 2))],
    [Variable(rand((2, 3))), onehot((2, 3))],
    [Variable(rand((1, 2))), onehot((1, 2))],
    [Variable(rand((2, 2, 3, 3))), onehot((2, 2, 3, 3))],
])
def test_softmax_cross_entropy(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return rm.softmax_cross_entropy(node, x)
    compare(func, node, node, x)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((1, 1))), Variable(randInteger((1, 1)))],
    [Variable(rand((2, 1))), Variable(randInteger((2, 1)))],
])
def test_sigmoid_cross_entropy(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return rm.sigmoid_cross_entropy(node, x)
    compare(func, node, node, x)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((1, 1))), rand((1, 1))],
    [Variable(rand((1, 3))), rand((1, 3))],
    [Variable(rand((2, 1))), rand((2, 1))],
    [Variable(rand((1, 1, 1, 2))), rand((1, 1, 1, 2))],
])
def test_mean_squared_error(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return rm.mean_squared_error(node, x)
    compare(func, node, node, x)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((1, 2))), Variable(randInteger((1, 2)))],
    [Variable(rand((2, 2))), Variable(randInteger((2, 2)))],
])
def test_cross_entropy(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return rm.cross_entropy(node, x)
    compare(func, node, node, x)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((2, 2))), Variable(rand((2, 2)))],
    [Variable(rand((2, 2))), Variable(rand((2, 1)))],
    [Variable(rand((2, 1))), Variable(rand((1, 1)))],
])
def test_dot(node, x, use_gpu):
    node = Variable(node)
    x = Variable(x)

    set_cuda_active(use_gpu)

    def func(node, x):
        return sum(rm.dot(node, x))
    compare(func, node, node, x)
    compare(func, x, node, x)


@pytest.mark.parametrize("node, x", [
    [Variable(rand((2, 2))), rand((2, 2))],
])
def test_where(node, x, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node, x):
        return sum(rm.where(node > 0.5, node, x))
    compare(func, node, node, x)


@pytest.mark.parametrize("node, axis", [
    [[Variable(rand((2, 1))), Variable(rand((2, 1)))], 0],
    [[Variable(rand((2, 1))), Variable(rand((2, 1)))], 1],
    [[Variable(rand((2, 1))), Variable(rand((2, 2)))], 1],
    [[Variable(rand((2, 1))), Variable(rand((2, 2))), Variable(rand((2, 2)))], 1],
    [[Variable(rand((2, 2, 2))), Variable(rand((2, 2, 1))), Variable(rand((2, 2, 3)))], 2],
])
def test_concat(node, axis, use_gpu):
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.concat(node, axis=axis))
    compare(func, node[0], node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 2, 1, 1))),
    Variable(rand((1, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1,))),
])
def test_abs(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(abs(node))
    compare(func, node, node)


@pytest.mark.parametrize("node, axis", [
    [Variable(rand((2, 2))), None],
    [Variable(rand((2, 2, 1, 1))), 2],
    [Variable(rand((2, 3, 4, 5))), 0],
    [Variable(rand((2, 3, 4, 5))), 1],
    [Variable(rand((2, 3, 4, 5))), 2],
    [Variable(rand((2, 3, 4, 5))), 3],
    [Variable(rand((1, 2))), 0],
    [Variable(rand((2, 1))), 1],
    [Variable(rand((1,))), 0],
])
def test_sum(node, axis, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(sum(node, axis=axis))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 2, 1, 1))),
    Variable(rand((1, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1,))),
])
def test_log(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.log(node))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((2, 2, 1, 1))),
    Variable(rand((1, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1,))),
])
def test_exp(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.exp(node))
    compare(func, node, node)


@pytest.mark.parametrize("node, shape", [
    [Variable(rand((2, 2))), (1, 4)],
    [Variable(rand((2, 2, 1, 1))), (4, 1)],
    [Variable(rand((1, 2))), (2, 1)],
    [Variable(rand((2, 1))), (1, 2)],
    [Variable(rand((1,))), (1,)],
])
def test_reshape(node, shape, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.reshape(node, shape)) + sum(node.reshape(shape)) + sum(node.reshape(*shape))
    compare(func, node, node)


@pytest.mark.parametrize("node", [
    Variable(rand((2, 2))),
    Variable(rand((1, 2))),
    Variable(rand((2, 1))),
    Variable(rand((1,))),
])
def test_T(node, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(node.T)
    compare(func, node, node)


@pytest.mark.parametrize("node, axis", [
    [Variable(rand((2, 2))), (1, 0)],
])
def test_transpose(node, axis, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(node.transpose(axis))
    compare(func, node, node)


@pytest.mark.parametrize("node, axis", [
    [Variable(rand((2, 2))), None],
    [Variable(rand((2, 2))), 0],
    [Variable(rand((2, 2))), 1],
    [Variable(rand((2, 2, 2))), 2],
])
def test_max(node, axis, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.amax(node, axis))
    compare(func, node, node)


@pytest.mark.parametrize("node, axis", [
    [Variable(rand((2, 2))), None],
    [Variable(rand((2, 2))), 0],
    [Variable(rand((2, 2))), 1],
    [Variable(rand((2, 2, 2))), 2],
])
def test_min(node, axis, use_gpu):
    node = Variable(node)
    set_cuda_active(use_gpu)

    def func(node):
        return sum(rm.amin(node, axis))
    compare(func, node, node)
