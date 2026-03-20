"""Result class for Plectrum SDK."""

from __future__ import annotations

import time as time_module
from typing import Any, Dict, Optional


class Result:
    """统一的结果类，用于标准化不同求解器的返回结果。"""

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
        oepo_time: float = None,
        e2e_time: float = None,
        solver_name: str = None,
    ):
        self._energy = energy
        self._spin_config = spin_config
        self._time = time
        self._task_id = task_id
        self._task_name = task_name
        self._ok = ok
        self._msg = msg
        self._timestamp = timestamp
        self._oepo_time = oepo_time if oepo_time is not None else time
        self._e2e_time = e2e_time if e2e_time is not None else self._oepo_time
        self._solver_name = solver_name

    @property
    def energy(self) -> float:
        """获取能量值。"""
        return self._energy

    @property
    def spin_config(self) -> list:
        """获取自旋配置列表。"""
        return self._spin_config

    @property
    def sping_config(self) -> list:
        """兼容历史拼写错误字段。"""
        return self._spin_config

    @property
    def time(self) -> float:
        """获取计算时间（秒）。"""
        return self._time

    @property
    def oepo_time(self) -> float:
        """获取求解器核心计算时间（秒）。"""
        return self._oepo_time

    @property
    def e2e_time(self) -> float:
        """获取端到端耗时（秒）。"""
        return self._e2e_time

    @property
    def task_id(self) -> str:
        """获取任务ID。"""
        return self._task_id

    @property
    def task_name(self) -> str:
        """获取任务名称。"""
        return self._task_name

    @property
    def name(self) -> str:
        """兼容示例中的名称字段访问。"""
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

    @property
    def solver_name(self) -> Optional[str]:
        """Get solver name if available."""
        return self._solver_name

    def to_dict(self) -> dict:
        """转换为字典格式。

        Returns:
            字典格式的结果
        """
        return {
            "energy": self._energy,
            "spin_config": self._spin_config,
            "sping_config": self._spin_config,
            "time": self._time,
            "oepo_time": self._oepo_time,
            "e2e_time": self._e2e_time,
            "task_id": self._task_id,
            "task_name": self._task_name,
            "name": self._task_name,
            "ok": self._ok,
            "msg": self._msg,
            "timestamp": self._timestamp,
            "solver_name": self._solver_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Result":
        """Create Result from an already normalized dictionary."""
        time_value = cls._parse_duration(data.get("time"))
        oepo_time = cls._parse_duration(data.get("oepo_time"))
        e2e_time = cls._parse_duration(data.get("e2e_time"))

        if time_value is None:
            time_value = oepo_time if oepo_time is not None else e2e_time
        if oepo_time is None:
            oepo_time = time_value
        if e2e_time is None:
            e2e_time = oepo_time

        return cls(
            energy=data.get("energy"),
            spin_config=data.get("spin_config") or data.get("sping_config"),
            time=time_value,
            oepo_time=oepo_time,
            e2e_time=e2e_time,
            task_id=data.get("task_id"),
            task_name=data.get("task_name") or data.get("name"),
            ok=data.get("ok", True),
            msg=data.get("msg"),
            timestamp=data.get("timestamp"),
            solver_name=data.get("solver_name"),
        )

    @classmethod
    def from_local(cls, raw_result: dict, task_id: str) -> "Result":
        """从本地求解器的原始结果创建 Result。

        Args:
            raw_result: 本地求解器返回的原始结果
            task_id: 任务ID

        Returns:
            Result 实例
        """
        result_data = raw_result.get("result", raw_result)

        time_ms = result_data.get("isingCalcMs")
        time_seconds = time_ms / 1000.0 if time_ms is not None else None

        return cls(
            energy=result_data.get("energy"),
            spin_config=result_data.get("spin_config")
            or result_data.get("sping_config"),
            time=time_seconds,
            oepo_time=time_seconds,
            e2e_time=time_seconds,
            task_id=task_id,
            task_name=result_data.get("taskName"),
            ok=result_data.get("ok", True),
            msg=result_data.get("msg"),
            timestamp=result_data.get("ts"),
            solver_name="LocalOepoSolver",
        )

    @classmethod
    def from_cloud(cls, raw_result: dict, task_id: str) -> "Result":
        """从云求解器的原始结果创建 Result。

        Args:
            raw_result: 云求解器返回的原始结果
            task_id: 任务ID

        Returns:
            Result 实例
        """
        time_seconds = cls._parse_duration(raw_result.get("oepo_time"))
        e2e_time = cls._parse_duration(raw_result.get("e2e_time"))
        if e2e_time is None:
            e2e_time = time_seconds

        return cls(
            energy=raw_result.get("energy"),
            spin_config=raw_result.get("spin_config")
            or raw_result.get("sping_config"),
            time=time_seconds,
            oepo_time=time_seconds,
            e2e_time=e2e_time,
            task_id=task_id,
            task_name=raw_result.get("task_name") or raw_result.get("name"),
            ok=raw_result.get("ok", True),
            msg=raw_result.get("msg", "success"),
            timestamp=raw_result.get("timestamp")
            or int(time_module.time() * 1000),
            solver_name="CloudSolver",
        )

    @classmethod
    def from_solver_response(
        cls,
        raw_response: Any,
        task_name: str = None,
    ) -> "Result":
        """Normalize a raw solver response into a Result object."""
        if isinstance(raw_response, cls):
            result = raw_response
        elif isinstance(raw_response, dict) and "result" in raw_response:
            data = raw_response.get("result") or {}
            if isinstance(data, cls):
                result = data
            else:
                result = cls.from_dict(data)
            if result._task_id is None:
                result._task_id = raw_response.get("task_id")
        elif isinstance(raw_response, dict):
            result = cls.from_dict(raw_response)
        else:
            raise TypeError(
                f"Unsupported solver response type: {type(raw_response).__name__}"
            )

        if task_name and (
            result._task_name is None
            or result._task_name == result._task_id
        ):
            result._task_name = task_name
        elif result._task_name is None:
            result._task_name = task_name
        return result

    @staticmethod
    def _parse_duration(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if value.endswith("ms"):
                return float(value[:-2]) / 1000.0
            if value.endswith("s"):
                return float(value[:-1])
            return float(value)
        return None

    def __repr__(self) -> str:
        return (
            f"Result(energy={self._energy}, "
            f"spin_config={self._spin_config}, "
            f"time={self._time}, "
            f"task_id={self._task_id})"
        )

    def __str__(self) -> str:
        return f"Result(energy={self._energy}, time={self._time}s)"
