"""Result class for Plectrum SDK."""


class Result:
    """Unified result class that standardizes solver outputs.

    Attributes:
        energy: Energy value of the solution
        spin_config: Spin / binary configuration list
        oepo_time: Solver computation time (seconds)
        e2e_time: End-to-end time including overhead (seconds)
        task_id: Task ID
        task_name: Task name
        name: Alias for task_name
        ok: Whether the solve succeeded
        msg: Status message
        timestamp: Timestamp in milliseconds
    """

    def __init__(
        self,
        energy: float = None,
        spin_config: list = None,
        oepo_time: float = None,
        e2e_time: float = None,
        task_id: str = None,
        task_name: str = None,
        ok: bool = True,
        msg: str = None,
        timestamp: int = None,
        # Backward compat alias
        time: float = None,
    ):
        self._energy = energy
        self._spin_config = spin_config
        # oepo_time takes precedence; fall back to legacy 'time' param
        self._oepo_time = oepo_time if oepo_time is not None else time
        self._e2e_time = e2e_time
        self._task_id = task_id
        self._task_name = task_name
        self._ok = ok
        self._msg = msg
        self._timestamp = timestamp

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def energy(self) -> float:
        """Energy value of the solution."""
        return self._energy

    @property
    def spin_config(self) -> list:
        """Spin / binary configuration list."""
        return self._spin_config

    @property
    def oepo_time(self) -> float:
        """Solver computation time (seconds)."""
        return self._oepo_time

    @property
    def e2e_time(self) -> float:
        """End-to-end time including all overhead (seconds)."""
        return self._e2e_time

    @property
    def time(self) -> float:
        """Computation time (seconds). Alias for oepo_time."""
        return self._oepo_time

    @property
    def task_id(self) -> str:
        """Task ID."""
        return self._task_id

    @property
    def task_name(self) -> str:
        """Task name."""
        return self._task_name

    @property
    def name(self) -> str:
        """Task name (convenience alias)."""
        return self._task_name

    @property
    def ok(self) -> bool:
        """Whether the solve succeeded."""
        return self._ok

    @property
    def msg(self) -> str:
        """Status message."""
        return self._msg

    @property
    def timestamp(self) -> int:
        """Timestamp in milliseconds."""
        return self._timestamp

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "energy": self._energy,
            "spin_config": self._spin_config,
            "oepo_time": self._oepo_time,
            "e2e_time": self._e2e_time,
            "task_id": self._task_id,
            "task_name": self._task_name,
            "ok": self._ok,
            "msg": self._msg,
            "timestamp": self._timestamp,
        }

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @classmethod
    def from_local(cls, raw_result: dict, task_id: str) -> "Result":
        """Create Result from local OEPO solver raw response.

        Expected format::

            {"job_name": "...", "result": {"energy": ..., "isingCalcMs": ...,
             "ok": ..., "spin_config": [...], "taskName": "...", "ts": ...}}
        """
        result_data = raw_result.get("result", {})

        time_ms = result_data.get("isingCalcMs")
        time_seconds = time_ms / 1000.0 if time_ms is not None else None

        return cls(
            energy=result_data.get("energy"),
            spin_config=result_data.get("spin_config"),
            oepo_time=time_seconds,
            task_id=task_id,
            task_name=result_data.get("taskName"),
            ok=result_data.get("ok", True),
            msg=result_data.get("msg"),
            timestamp=result_data.get("ts"),
        )

    @classmethod
    def from_cloud(cls, raw_result: dict, task_id: str) -> "Result":
        """Create Result from cloud solver raw response.

        Expected format::

            {"energy": ..., "spin_config": [...], "oepo_time": "0.134s", ...}
        """
        time_val = raw_result.get("oepo_time")
        time_seconds = None
        if time_val is not None:
            if isinstance(time_val, str):
                time_seconds = float(time_val.replace("s", ""))
            else:
                time_seconds = float(time_val)

        import time as time_module

        return cls(
            energy=raw_result.get("energy"),
            spin_config=raw_result.get("spin_config"),
            oepo_time=time_seconds,
            task_id=task_id,
            task_name=None,
            ok=True,
            msg="success",
            timestamp=int(time_module.time() * 1000),
        )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Result(energy={self._energy}, "
            f"spin_config={self._spin_config}, "
            f"oepo_time={self._oepo_time}, "
            f"e2e_time={self._e2e_time}, "
            f"task_id={self._task_id})"
        )

    def __str__(self) -> str:
        return (
            f"Result(energy={self._energy}, "
            f"oepo_time={self._oepo_time}s, "
            f"e2e_time={self._e2e_time}s)"
        )
