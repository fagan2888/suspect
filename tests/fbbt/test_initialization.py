# pylint: skip-file
import pytest
from tests.conftest import PlaceholderExpression
import suspect.dag.expressions as dex
from suspect.interval import Interval
from suspect.fbbt.initialization import BoundsInitializationVisitor


@pytest.fixture
def visitor():
    return BoundsInitializationVisitor()


def _visit(visitor, root_cls):
    p = PlaceholderExpression()
    root = root_cls([p])
    ctx = {}
    visitor.visit(root, ctx)
    return ctx[p]


def test_sqrt(visitor):
    assert _visit(visitor, dex.SqrtExpression).is_nonnegative()


def test_log(visitor):
    assert _visit(visitor, dex.LogExpression).is_nonnegative()


def test_asin(visitor):
    assert _visit(visitor, dex.AsinExpression) == Interval(-1, 1)


def test_acos(visitor):
    assert _visit(visitor, dex.AcosExpression) == Interval(-1, 1)