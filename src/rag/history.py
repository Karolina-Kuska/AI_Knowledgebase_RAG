from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple


_HISTORY: Dict[str, Deque[Tuple[str, str]]] = defaultdict(lambda: deque(maxlen=10))

def get_history(session_id: str) -> List[Tuple[str, str]]:
    return list(_HISTORY[session_id])

def append_turn(session_id: str, user_msg: str, bot_msg: str) -> None:
    _HISTORY[session_id].append((user_msg, bot_msg))

def clear_history(session_id: str) -> None:
    _HISTORY.pop(session_id, None)
