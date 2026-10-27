"""Unit tests for ASTInvariantGate."""

from codeslim.optimizer.ast_guard import ASTInvariantGate


def test_ast_guard_valid_refactor() -> None:
    """Test valid refactor where signatures and decorators are preserved."""
    gate = ASTInvariantGate()
    orig = '''class MathOps:
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b
'''
    refactored = '''class MathOps:
    @staticmethod
    def add(a: int, b: int) -> int:
        # Optimised return
        return a + b
'''
    assert gate.is_safe(orig, refactored) is True


def test_ast_guard_decorator_mutation_rejected() -> None:
    """Test rejecting decorator removal (@staticmethod removed)."""
    gate = ASTInvariantGate()
    orig = '''class Foo:
    @staticmethod
    def bar(a: int) -> int:
        return a
'''
    patched = '''class Foo:
    def bar(a: int) -> int:
        return a
'''
    assert gate.is_safe(orig, patched) is False


def test_ast_guard_async_mutation_rejected() -> None:
    """Test rejecting conversion from async def to def."""
    gate = ASTInvariantGate()
    orig = "async def fetch_data(url: str) -> str: pass"
    patched = "def fetch_data(url: str) -> str: pass"
    assert gate.is_safe(orig, patched) is False


def test_ast_guard_missing_signature_rejected() -> None:
    """Test rejecting removal of a public function."""
    gate = ASTInvariantGate()
    orig = "def public_api(): pass\ndef helper(): pass"
    patched = "def helper(): pass"
    assert gate.is_safe(orig, patched) is False


def test_ast_guard_validate_diagnostics() -> None:
    """Test validate() returning specific diagnostic messages for mutations."""
    gate = ASTInvariantGate()
    orig = "@staticmethod\ndef calculate(x: int) -> int: return x"
    patched = "def calculate(x: int, extra: int) -> int: return x"

    is_safe, violations = gate.validate(orig, patched)
    assert is_safe is False
    assert len(violations) >= 2
    assert any("Decorators mutated" in v for v in violations)
    assert any("Signature arguments mutated" in v for v in violations)

