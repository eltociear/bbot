import csv
from contextlib import suppress

from bbot.modules.output.base import BaseOutputModule


class CSV(BaseOutputModule):
    watched_events = ["*"]
    meta = {"description": "Output to CSV"}
    options = {"output_file": ""}
    options_desc = {"output_file": "Output to CSV file"}

    header_row = ["Event type", "Event data", "IP Address", "Source Module", "Scope Distance", "Event Tags"]
    filename = "output.csv"

    def setup(self):
        self._writer = None
        self._prep_output_dir(self.filename)
        return True

    @property
    def writer(self):
        file_exists = self.output_file.is_file()
        if self._writer is None:
            self._writer = csv.DictWriter(self.file, fieldnames=self.header_row)
            if not file_exists:
                self._writer.writeheader()
        return self._writer

    @property
    def file(self):
        if self._file is None:
            if self.output_file.is_file():
                self.helpers.backup_file(self.output_file)
            self._file = open(self.output_file, mode="a", newline="")
        return self._file

    def writerow(self, row):
        self.writer.writerow(row)
        self.file.flush()

    def handle_event(self, event):
        self.writerow(
            {
                "Event type": getattr(event, "type", ""),
                "Event data": getattr(event, "data", ""),
                "IP Address": ",".join(
                    str(x) for x in getattr(event, "resolved_hosts", set()) if self.helpers.is_ip(x)
                ),
                "Source Module": str(getattr(event, "module", "")),
                "Scope Distance": str(getattr(event, "scope_distance", "")),
                "Event Tags": ",".join(sorted(list(getattr(event, "tags", [])))),
            }
        )

    def cleanup(self):
        if getattr(self, "_file", None) is not None:
            with suppress(Exception):
                self.file.close()

    def report(self):
        if self._file is not None:
            self.info(f"Saved CSV output to {self.output_file}")
