"""
Tokenizer & Token Budget Engine for CodeSlim.

Provides token estimation, encoding lookup, and budget enforcement
with graceful fallback to heuristic estimation if tiktoken fails.
"""

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.context.tokenizer")

try:
    import tiktoken

    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    log.warning("tiktoken_not_installed_using_fallback")


def count_tokens(text: str, model_or_encoding: str = "cl100k_base") -> int:
    """
    Count exact token length using tiktoken with fallback heuristic.

    Args:
        text: Input string.
        model_or_encoding: Encoding name (e.g. 'cl100k_base') or model name.

    Returns:
        Estimated or exact token count.
    """
    if not text.strip():
        return 0

    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.get_encoding(model_or_encoding)
            return len(encoding.encode(text))
        except Exception:
            try:
                encoding = tiktoken.encoding_for_model(model_or_encoding)
                return len(encoding.encode(text))
            except Exception as exc:
                log.debug("tiktoken_lookup_failed_using_fallback", error=str(exc))

    # Fallback heuristic: ~4 characters per token for typical Python source code
    return len(text) // 4


def enforce_token_budget(text: str, max_tokens: int, model_or_encoding: str = "cl100k_base") -> str:
    """
    Enforce a maximum token budget on text.
    If text exceeds max_tokens, truncates safely with a notice marker.

    Args:
        text: Input source code or text.
        max_tokens: Maximum allowed token budget.
        model_or_encoding: Model or encoding identifier.

    Returns:
        Truncated or unmodified text string.
    """
    current_tokens = count_tokens(text, model_or_encoding)
    if current_tokens <= max_tokens:
        return text

    log.info("token_budget_exceeded", current=current_tokens, max=max_tokens)

    # Estimate character limit needed for max_tokens
    char_ratio = len(text) / max(current_tokens, 1)
    target_chars = int(max_tokens * char_ratio * 0.95)  # 5% safety margin

    truncated = text[:target_chars]
    marker = "\n# ... [CodeSlim Context Minimizer: Content truncated to fit token budget] ...\n"
    return truncated + marker
