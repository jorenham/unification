from types import MappingProxyType

from unification import var
from unification.core import reify, unify, unground_lvars


def test_reify():
    x, y, z = var(), var(), var()
    s = {x: 1, y: 2, z: (x, y)}
    assert reify(x, s) == 1
    assert reify(10, s) == 10
    assert reify((1, y), s) == (1, 2)
    assert reify((1, (x, (y, 2))), s) == (1, (1, (2, 2)))
    assert reify(z, s) == (1, 2)
    assert reify(z, MappingProxyType(s)) == (1, 2)


def test_reify_dict():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = {1: x, 3: {5: y}}
    assert reify(e, s) == {1: 2, 3: {5: 4}}


def test_reify_list():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = [1, [x, 3], y]
    assert reify(e, s) == [1, [2, 3], 4]


def test_reify_complex():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = {1: [x], 3: (y, 5)}

    assert reify(e, s) == {1: [2], 3: (4, 5)}


def test_unify_slice():
    x = var("x")
    y = var("y")

    assert unify(slice(1), slice(1), {}) == {}
    assert unify(slice(1, 2, 3), x, {}) == {x: slice(1, 2, 3)}
    assert unify(slice(1, 2, None), slice(x, y), {}) == {x: 1, y: 2}


def test_reify_slice():
    assert reify(slice(1, var(2), 3), {var(2): 10}) == slice(1, 10, 3)


def test_unify():
    assert unify(1, 1, {}) == {}
    assert unify(1, 2, {}) is False
    assert unify(var(1), 2, {}) == {var(1): 2}
    assert unify(2, var(1), {}) == {var(1): 2}
    assert unify(2, var(1), MappingProxyType({})) == {var(1): 2}


def test_iter():
    assert unify([1], (1,)) is False
    assert unify((i for i in [1, 2]), [1, 2]) is False


def test_unify_seq():
    assert unify((1, 2), (1, 2), {}) == {}
    assert unify([1, 2], [1, 2], {}) == {}
    assert unify((1, 2), (1, 2, 3), {}) is False
    assert unify((1, var(1)), (1, 2), {}) == {var(1): 2}
    assert unify((1, var(1)), (1, 2), {var(1): 3}) is False


def test_unify_set():
    x = var("x")
    assert unify(set((1, 2)), set((1, 2)), {}) == {}
    assert unify(set((1, x)), set((1, 2)), {}) == {x: 2}
    assert unify(set((x, 2)), set((1, 2)), {}) == {x: 1}


def test_unify_dict():
    assert unify({1: 2}, {1: 2}, {}) == {}
    assert unify({1: 2}, {1: 3}, {}) is False
    assert unify({2: 2}, {1: 2}, {}) is False
    assert unify({2: 2, 3: 3}, {1: 2}, {}) is False
    assert unify({1: var(5)}, {1: 2}, {}) == {var(5): 2}


def test_unify_complex():
    assert unify((1, {2: 3}), (1, {2: 3}), {}) == {}
    assert unify((1, {2: 3}), (1, {2: 4}), {}) is False
    assert unify((1, {2: var(5)}), (1, {2: 4}), {}) == {var(5): 4}

    assert unify({1: (2, 3)}, {1: (2, var(5))}, {}) == {var(5): 3}
    assert unify({1: [2, 3]}, {1: [2, var(5)]}, {}) == {var(5): 3}


def test_unground_lvars():
    assert unground_lvars((1, 2), {}) == set()
    assert unground_lvars((1, [var("a"), [var("b"), 2], 3]), {}) == {var("a"), var("b")}
    assert unground_lvars((1, [var("a"), [var("b"), 2], 3]), {var("a"): 4}) == {
        var("b")
    }
    assert (
        unground_lvars((1, [var("a"), [var("b"), 2], 3]), {var("a"): 4, var("b"): 5})
        == set()
    )
