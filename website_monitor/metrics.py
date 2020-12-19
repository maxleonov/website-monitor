from datetime import datetime
from typing import NamedTuple, Optional

import website_monitor.website_availability_metrics_pb2 as pb


class WebsiteAvailabilityMetrics(NamedTuple):
    datetime: datetime
    target: str
    http_response_time: float
    http_status: int
    regexp_match: Optional[bool] = None

    def serialize(self) -> str:
        data = pb.WebsiteAvailabilityMetrics()
        data.datetime.FromDatetime(self.datetime)
        data.target = self.target
        data.http_response_time = self.http_response_time
        data.http_status = self.http_status
        if self.regexp_match is None:
            data.regexp_match_null = True
        else:
            data.regexp_match_value = self.regexp_match
        return data.SerializeToString()

    @staticmethod
    def deserialize(data: str) -> "WebsiteAvailabilityMetrics":
        data_ = pb.WebsiteAvailabilityMetrics()
        data_.ParseFromString(data)
        return WebsiteAvailabilityMetrics(
            datetime=data_.datetime.ToDatetime(),
            target=data_.target,
            http_response_time=data_.http_response_time,
            http_status=data_.http_status,
            regexp_match=data_.regexp_match_value
            if not data_.regexp_match_null
            else None,
        )
