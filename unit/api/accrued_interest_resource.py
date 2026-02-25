from unit.api.base_resource import BaseResource
from unit.models.accrued_interest import *
from unit.models.codecs import DtoDecoder


class AccruedInterestResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "accrued-interest"

    def total(self, params: GetAccruedInterestTotalParams = None) -> Union[UnitResponse[AccruedInterestTotalDTO], UnitError]:
        params = params or GetAccruedInterestTotalParams()
        response = super().get(f"{self.resource}/total", params.to_dict())
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[AccruedInterestTotalDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())
