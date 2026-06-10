from unit.api.base_resource import BaseResource
from unit.models.codecs import DtoDecoder
from unit.models.dispute import *



class DisputeResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "disputes"

    def get(self, dispute_id: str) -> Union[UnitResponse[DisputeDTO], UnitError]:
        response = super().get(f"{self.resource}/{dispute_id}")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[DisputeDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def sandbox_create_dispute(self, request: SimulateDisputeRequest) -> Union[UnitResponse[DisputeDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"sandbox/{self.resource}", payload)
        return self.__handle_dispute_response(response)

    def sandbox_credit_provisionally(self, dispute_id: str) -> Union[UnitResponse[DisputeDTO], UnitError]:
        response = super().post(f"sandbox/{self.resource}/{dispute_id}/credit-provisionally")
        return self.__handle_dispute_response(response)

    def sandbox_resolve_won(self, dispute_id: str) -> Union[UnitResponse[DisputeDTO], UnitError]:
        response = super().post(f"sandbox/{self.resource}/{dispute_id}/resolve-won")
        return self.__handle_dispute_response(response)

    def sandbox_resolve_lost(self, dispute_id: str) -> Union[UnitResponse[DisputeDTO], UnitError]:
        response = super().post(f"sandbox/{self.resource}/{dispute_id}/resolve-lost")
        return self.__handle_dispute_response(response)

    def sandbox_deny(self, dispute_id: str) -> Union[UnitResponse[DisputeDTO], UnitError]:
        response = super().post(f"sandbox/{self.resource}/{dispute_id}/deny")
        return self.__handle_dispute_response(response)

    def __handle_dispute_response(self, response) -> Union[UnitResponse[DisputeDTO], UnitError]:
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[DisputeDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())
