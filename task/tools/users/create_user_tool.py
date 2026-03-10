from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return 'create_user'

    @property
    def description(self) -> str:
        return "Tool for creating a new user. It accepts user information as parameters and returns the created user details."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "title": "UserCreate",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "surname": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": ["string", "null"]},
                "date_of_birth": {"type": ["string", "null"]},
                "address": {"$ref": "#/definitions/Address"},
                "gender": {"type": ["string", "null"]},
                "company": {"type": ["string", "null"]},
                "salary": {"type": ["number", "null"]},
                "about_me": {"type": "string"},
                "credit_card": {"$ref": "#/definitions/CreditCard"}
            },
            "required": ["name", "surname", "email", "about_me"],
            "definitions": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string"},
                        "city": {"type": "string"},
                        "street": {"type": "string"},
                        "flat_house": {"type": "string"}
                    },
                    "required": ["country", "city", "street", "flat_house"]
                },
                "CreditCard": {
                    "type": "object",
                    "properties": {
                        "num": {"type": "string"},
                        "cvv": {"type": "string"},
                        "exp_date": {"type": "string"}
                    },
                    "required": ["num", "cvv", "exp_date"]
                }
            }

        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # 1. Validate arguments with `UserCreate.model_validate`
        # 2. Call user_client add user and return its results
        # 3. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
        print(f"=> Excuting {self.name} with arguments: {arguments}")
        user_model = UserCreate.model_validate(arguments)
        self._user_client.add_user(user_model)
