from ipaddress import ip_address
from math import isfinite
import httpx
from app.config import settings

class PrometheusQueryError(RuntimeError):

    pass


class PrometheusClient:
    def __init__(self) -> None:
        self.base_url = (
            settings.prometheus_url.rstrip("/")
        )

        self.timeout = (
            settings.prometheus_timeout_seconds
        )

    def query_vector(
        self,
        promql: str,
    ) -> list[dict]:

        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/query",
                params={
                    "query": promql,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            payload = response.json()

        except (
            httpx.HTTPError,
            ValueError,
        ) as exc:
            raise PrometheusQueryError(
                "Unable to communicate with Prometheus."
            ) from exc

        if payload.get("status") != "success":
            raise PrometheusQueryError(
                "Prometheus returned an unsuccessful response."
            )

        data = payload.get(
            "data",
            {},
        )

        if data.get("resultType") != "vector":
            raise PrometheusQueryError(
                "Prometheus returned an unexpected "
                "result type."
            )

        result = data.get(
            "result",
            [],
        )

        if not isinstance(
            result,
            list,
        ):
            raise PrometheusQueryError(
                "Prometheus returned invalid result data."
            )

        return result

    def health(self) -> bool:

        self.query_vector(
            "vector(1)"
        )

        return True

    @staticmethod
    def build_windows_instance(
        address: str,
    ) -> str:
    
        parsed = ip_address(
            address
        )

        if parsed.version == 6:
            host = f"[{address}]"
        else:
            host = address

        return (
            f"{host}:"
            f"{settings.windows_exporter_port}"
        )

    @staticmethod
    def escape_label_value(
        value: str,
    ) -> str:

        return (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

    @staticmethod
    def sample_value(
        result: dict,
    ) -> float | None:
        value_data = result.get(
            "value"
        )

        if (
            not isinstance(value_data, list)
            or len(value_data) < 2
        ):
            return None

        try:
            value = float(
                value_data[1]
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if not isfinite(value):
            return None

        return value

    def query_single_value(
        self,
        promql: str,
    ) -> float | None:
        results = self.query_vector(
            promql
        )

        if not results:
            return None

        return self.sample_value(
            results[0]
        )

    def cpu_percent(
        self,
        instance: str,
    ) -> float | None:
        instance = self.escape_label_value(
            instance
        )

        query = (
            "100 - ("
            "avg by (instance) ("
            "irate("
            "windows_cpu_time_total{"
            f'instance="{instance}",'
            'mode="idle"'
            "}[2m]"
            ")"
            ") * 100"
            ")"
        )

        value = self.query_single_value(
            query
        )

        if value is None:
            return None

        return round(
            max(
                0.0,
                min(
                    value,
                    100.0,
                ),
            ),
            2,
        )

    def memory_percent(
        self,
        instance: str,
    ) -> float | None:
        instance = self.escape_label_value(
            instance
        )

        query = (
            "100 * (1 - ("
            "windows_memory_physical_free_bytes{"
            f'instance="{instance}"'
            "}"
            " / "
            "windows_memory_physical_total_bytes{"
            f'instance="{instance}"'
            "}"
            "))"
        )

        value = self.query_single_value(
            query
        )

        if value is None:
            return None

        return round(
            max(
                0.0,
                min(
                    value,
                    100.0,
                ),
            ),
            2,
        )

    def disk_usage(
        self,
        instance: str,
    ) -> list[dict]:
        escaped_instance = (
            self.escape_label_value(
                instance
            )
        )

        query = (
            "100 - 100 * ("
            "windows_logical_disk_free_bytes{"
            f'instance="{escaped_instance}",'
            'volume=~"[A-Za-z]:"'
            "}"
            " / "
            "windows_logical_disk_size_bytes{"
            f'instance="{escaped_instance}",'
            'volume=~"[A-Za-z]:"'
            "}"
            ")"
        )

        results = self.query_vector(
            query
        )

        disks = []

        for result in results:
            value = self.sample_value(
                result
            )

            if value is None:
                continue

            metric = result.get(
                "metric",
                {},
            )

            volume = metric.get(
                "volume",
                "unknown",
            )

            disks.append(
                {
                    "volume": volume,
                    "used_percent": round(
                        max(
                            0.0,
                            min(
                                value,
                                100.0,
                            ),
                        ),
                        2,
                    ),
                }
            )

        disks.sort(
            key=lambda item: item["volume"]
        )

        return disks

prometheus_client = PrometheusClient()