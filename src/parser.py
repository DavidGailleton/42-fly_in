from pathlib import Path
import re
from typing import Any
from src.classes.Exceptions import ParseError
from src.classes.Models import MapConfig, ZoneType, Hub, Connection, Colors


class MapParser:
    """Parser for drone map files."""

    def __init__(self) -> None:
        self._hubs: list[Hub] = []
        self._connections: list[Connection] = []
        self._nb_drones: int | None = None
        self._start_hub: str | None = None
        self._end_hub: str | None = None

    def parse_file(self, file_path: Path) -> MapConfig:
        """Parse a map file and return a validated MapConfig."""
        self._reset()

        first_content_line_seen = False

        try:
            with open(file_path, encoding="utf-8") as file:
                for line_number, raw_line in enumerate(file, start=1):
                    line = self._clean_line(raw_line)
                    if line is None:
                        continue

                    if not first_content_line_seen:
                        first_content_line_seen = True
                        self._validate_first_line(line, line_number)

                    self._parse_line(line, line_number)

            return self._build_config()

        except OSError as err:
            raise ParseError(
                f"Could not open file '{file_path}': {err}"
            ) from err

    def _reset(self) -> None:
        """Reset parser state before parsing a new file."""
        self._hubs = []
        self._connections = []
        self._nb_drones = None
        self._start_hub = None
        self._end_hub = None

    def _clean_line(self, raw_line: str) -> str | None:
        """Strip spaces and ignore empty/comment-only lines."""
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return None
        return line

    def _validate_first_line(self, line: str, line_number: int) -> None:
        """Ensure the first non-comment line defines nb_drones."""
        if not line.startswith("nb_drones:"):
            raise ParseError(
                f"Line {line_number}: first non-comment line must be "
                f"'nb_drones: <positive_integer>'"
            )

    def _parse_line(self, line: str, line_number: int) -> None:
        """Dispatch line parsing depending on its prefix."""
        if line.startswith("nb_drones:"):
            self._parse_nb_drones(line, line_number)
        elif line.startswith("start_hub:"):
            self._parse_hub_line(line, line_number, hub_kind="start")
        elif line.startswith("end_hub:"):
            self._parse_hub_line(line, line_number, hub_kind="end")
        elif line.startswith("hub:"):
            self._parse_hub_line(line, line_number, hub_kind="normal")
        elif line.startswith("connection:"):
            self._parse_connection_line(line, line_number)
        else:
            raise ParseError(f"Line {line_number}: unknown line type")

    def _parse_nb_drones(self, line: str, line_number: int) -> None:
        """Parse the drone count line."""
        if self._nb_drones is not None:
            raise ParseError(
                f"Line {line_number}: multiple definition of nb_drones"
            )

        value = line.removeprefix("nb_drones:").strip()
        try:
            nb_drones = int(value)
        except ValueError as err:
            raise ParseError(
                f"Line {line_number}: nb_drones must be an integer"
            ) from err

        if nb_drones <= 0:
            raise ParseError(
                f"Line {line_number}: nb_drones must be a positive integer"
            )

        self._nb_drones = nb_drones

    def _parse_hub_line(
        self,
        line: str,
        line_number: int,
        hub_kind: str,
    ) -> None:
        """Parse a start_hub, end_hub, or regular hub line."""
        prefix = self._get_hub_prefix(hub_kind)
        content = line.removeprefix(prefix).strip()

        metadata = self._extract_metadata(content, line_number)
        content_without_metadata = self._remove_metadata(content).strip()
        parts = content_without_metadata.split()

        if len(parts) != 3:
            raise ParseError(
                f"Line {line_number}: invalid hub definition, expected "
                f"'<name> <x> <y> [metadata]'"
            )

        name = parts[0]
        x_str = parts[1]
        y_str = parts[2]

        self._validate_hub_name(name, line_number)
        self._ensure_hub_name_is_unique(name, line_number)

        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError as err:
            raise ParseError(
                f"Line {line_number}: hub coordinates must be integers"
            ) from err

        hub_data: dict[str, Any] = {
            "name": name,
            "coordinate": (x, y),
        }
        hub_data.update(metadata)

        hub = Hub(**hub_data)
        self._hubs.append(hub)

        if hub_kind == "start":
            if self._start_hub is not None:
                raise ParseError(
                    f"Line {line_number}: multiple definition of start_hub"
                )
            self._start_hub = hub.name

        elif hub_kind == "end":
            if self._end_hub is not None:
                raise ParseError(
                    f"Line {line_number}: multiple definition of end_hub"
                )
            self._end_hub = hub.name

    def _parse_connection_line(self, line: str, line_number: int) -> None:
        """Parse a connection line."""
        content = line.removeprefix("connection:").strip()

        metadata = self._extract_metadata(content, line_number)
        content_without_metadata = self._remove_metadata(content).strip()

        parts = content_without_metadata.split()
        if len(parts) != 1:
            raise ParseError(
                f"Line {line_number}: invalid connection definition"
            )

        if "-" not in parts[0]:
            raise ParseError(
                f"Line {line_number}: connection must use '<hub1>-<hub2>' syntax"
            )

        hub1, hub2 = parts[0].split("-", 1)

        if not hub1 or not hub2:
            raise ParseError(
                f"Line {line_number}: invalid connection hub names"
            )

        self._ensure_hub_exists(hub1, line_number)
        self._ensure_hub_exists(hub2, line_number)

        normalized_hubs = tuple(sorted((hub1, hub2)))
        self._ensure_connection_is_unique(normalized_hubs, line_number)

        connection_data: dict[str, Any] = {
            "hubs": normalized_hubs,
        }
        connection_data.update(metadata)

        connection = Connection(**connection_data)
        self._connections.append(connection)

    def _extract_metadata(
        self,
        content: str,
        line_number: int,
    ) -> dict[str, str | int | ZoneType]:
        """Extract and validate optional metadata block."""
        matches = re.findall(r"\[([^\]]+)\]", content)

        if len(matches) > 1:
            raise ParseError(
                f"Line {line_number}: multiple metadata blocks are not allowed"
            )
        if len(matches) == 0:
            return {}

        raw_metadata = matches[0]
        metadata: dict[str, str | int | ZoneType] = {}
        allowed_keys = {"zone", "color", "max_drones", "max_link_capacity"}

        for token in raw_metadata.split():
            if "=" not in token:
                raise ParseError(
                    f"Line {line_number}: invalid metadata entry '{token}'"
                )

            key, value = token.split("=", 1)

            if key not in allowed_keys:
                raise ParseError(
                    f"Line {line_number}: unknown metadata key '{key}'"
                )
            if key in metadata:
                raise ParseError(
                    f"Line {line_number}: duplicate metadata key '{key}'"
                )

            metadata[key] = self._convert_metadata_value(
                key, value, line_number
            )

        return metadata

    def _convert_metadata_value(
        self,
        key: str,
        value: str,
        line_number: int,
    ) -> str | int | ZoneType | Colors:
        """Convert one metadata value to its typed form."""
        if key == "zone":
            zone_map = {
                "normal": ZoneType.NORMAL,
                "blocked": ZoneType.BLOCKED,
                "restricted": ZoneType.RESTRICTED,
                "priority": ZoneType.PRIORITY,
            }
            if value not in zone_map:
                raise ParseError(
                    f"Line {line_number}: invalid zone type '{value}'"
                )
            return zone_map[value]

        if key == "color":
            color_map = {str(color.name).lower(): color for color in Colors}
            if value not in color_map:
                return color_map["red"]
            return color_map[value]

        if key in {"max_drones", "max_link_capacity"}:
            try:
                parsed_value = int(value)
            except ValueError as err:
                raise ParseError(
                    f"Line {line_number}: '{key}' must be an integer"
                ) from err

            if parsed_value <= 0:
                raise ParseError(
                    f"Line {line_number}: '{key}' must be a positive integer"
                )
            return parsed_value

        return value

    def _remove_metadata(self, content: str) -> str:
        """Remove metadata block from content."""
        return re.sub(r"\[[^\]]+\]", "", content)

    def _validate_hub_name(self, name: str, line_number: int) -> None:
        """Validate hub name format."""
        if " " in name or "-" in name:
            raise ParseError(
                f"Line {line_number}: hub name '{name}' cannot contain spaces or dashes"
            )

    def _ensure_hub_name_is_unique(self, name: str, line_number: int) -> None:
        """Ensure no hub with the same name already exists."""
        for hub in self._hubs:
            if hub.name == name:
                raise ParseError(
                    f"Line {line_number}: duplicate hub name '{name}'"
                )

    def _ensure_hub_exists(self, name: str, line_number: int) -> None:
        """Ensure a connection only references already defined hubs."""
        for hub in self._hubs:
            if hub.name == name:
                return
        raise ParseError(f"Line {line_number}: unknown hub '{name}'")

    def _ensure_connection_is_unique(
        self,
        hubs: tuple[str, str],
        line_number: int,
    ) -> None:
        """Ensure a connection does not already exist."""
        for connection in self._connections:
            if connection.hubs == hubs:
                raise ParseError(
                    f"Line {line_number}: duplicate connection '{hubs[0]}-{hubs[1]}'"
                )

    def _get_hub_prefix(self, hub_kind: str) -> str:
        """Return the expected prefix for the hub kind."""
        if hub_kind == "start":
            return "start_hub:"
        if hub_kind == "end":
            return "end_hub:"
        return "hub:"

    def _build_config(self) -> MapConfig:
        """Build final MapConfig after full validation."""
        if self._nb_drones is None:
            raise ParseError("Missing nb_drones")
        if self._start_hub is None:
            raise ParseError("Missing start_hub")
        if self._end_hub is None:
            raise ParseError("Missing end_hub")

        return MapConfig(
            nb_drones=self._nb_drones,
            start_hub=self._start_hub,
            end_hub=self._end_hub,
            hubs=self._hubs,
            connections=self._connections,
        )
