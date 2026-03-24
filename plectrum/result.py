"""Result class for Plectrum SDK."""

from plectrum.exceptions import ClientError


class Result:
    """Unified result class for standardizing solver outputs.

    Attributes:
        energy: Energy value
        spin_config: Spin configuration list
        time: Computation time (seconds)
        task_id: Task ID
        task_name: Task name
        ok: Whether the task succeeded
        msg: Status message
        timestamp: Timestamp (milliseconds)
    """

    def __init__(
        self,
        energy: float = None,
        spin_config: list = None,
        time: float = None,
        task_id: str = None,
        task_name: str = None,
        ok: bool = True,
        msg: str = None,
        timestamp: int = None,
    ):
        self._energy = energy
        self._spin_config = spin_config
        self._time = time
        self._task_id = task_id
        self._task_name = task_name
        self._ok = ok
        self._msg = msg
        self._timestamp = timestamp

    @property
    def energy(self) -> float:
        """获取能量值。"""
        return self._energy

    @property
    def spin_config(self) -> list:
        """获取自旋配置列表。"""
        return self._spin_config

    @property
    def time(self) -> float:
        """获取计算时间（秒）。"""
        return self._time

    @property
    def task_id(self) -> str:
        """获取任务ID。"""
        return self._task_id

    @property
    def task_name(self) -> str:
        """获取任务名称。"""
        return self._task_name

    @property
    def ok(self) -> bool:
        """获取是否成功。"""
        return self._ok

    @property
    def msg(self) -> str:
        """获取消息。"""
        return self._msg

    @property
    def timestamp(self) -> int:
        """获取时间戳（毫秒）。"""
        return self._timestamp

    def to_dict(self) -> dict:
        """转换为字典格式。

        Returns:
            字典格式的结果
        """
        return {
            "energy": self._energy,
            "spin_config": self._spin_config,
            "time": self._time,
            "task_id": self._task_id,
            "task_name": self._task_name,
            "ok": self._ok,
            "msg": self._msg,
            "timestamp": self._timestamp,
        }

    @classmethod
    def from_local(cls, raw_result: dict, task_id: str) -> "Result":
        """从本地求解器的原始结果创建 Result。

        Args:
            raw_result: 本地求解器返回的原始结果
            task_id: 任务ID

        Returns:
            Result 实例

        Raises:
            ClientError: If *raw_result* is not a dict or contains
                unparseable fields.
        """
        if not isinstance(raw_result, dict):
            raise ClientError(
                f"Expected dict for local result, got {type(raw_result).__name__}"
            )

        try:
            result_data = raw_result.get("result", {})
            time_ms = result_data.get("isingCalcMs")
            time_seconds = time_ms / 1000.0 if time_ms is not None else None

            return cls(
                energy=result_data.get("energy"),
                spin_config=result_data.get("spin_config"),
                time=time_seconds,
                task_id=task_id,
                task_name=result_data.get("taskName"),
                ok=result_data.get("ok", True),
                msg=result_data.get("msg"),
                timestamp=result_data.get("ts"),
            )
        except (TypeError, KeyError, ValueError) as e:
            raise ClientError(f"Failed to parse local result: {e}") from e

    @classmethod
    def from_cloud(cls, raw_result: dict, task_id: str) -> "Result":
        """从云求解器的原始结果创建 Result。

        Args:
            raw_result: 云求解器返回的原始结果
            task_id: 任务ID

        Returns:
            Result 实例

        Raises:
            ClientError: If *raw_result* is not a dict or contains
                unparseable fields.
        """
        if not isinstance(raw_result, dict):
            raise ClientError(
                f"Expected dict for cloud result, got {type(raw_result).__name__}"
            )

        time_str = raw_result.get("oepo_time")
        time_seconds = None
        if time_str and isinstance(time_str, str):
            try:
                time_seconds = float(time_str.replace("s", ""))
            except ValueError as e:
                raise ClientError(f"Invalid oepo_time format: {time_str!r}") from e

        import time as time_module

        return cls(
            energy=raw_result.get("energy"),
            spin_config=raw_result.get("spin_config"),
            time=time_seconds,
            task_id=task_id,
            task_name=None,
            ok=True,
            msg="success",
            timestamp=int(time_module.time() * 1000),
        )

    def __eq__(self, other):
        if not isinstance(other, Result):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return (
            f"Result(energy={self._energy}, "
            f"spin_config={self._spin_config}, "
            f"time={self._time}, "
            f"task_id={self._task_id})"
        )

    def __str__(self) -> str:
        return f"Result(energy={self._energy}, time={self._time}s)"
