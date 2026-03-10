from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "update_user"

    @property
    def description(self) -> str:
        return "Tool for updating existing user information. It accepts user ID and new user information as parameters and returns the updated user details."

    @property
    def input_schema(self) -> dict[str, Any]:

        # Provide tool params Schema:
        # - id: number, required, User ID that should be updated.
        # - new_info: UserUpdate.model_json_schema()
        return {
            "title": "UserUpdate",
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Unique identifier of the user to retrieve",
                    "minimum": 0
                },
                "new_info": UserUpdate.model_json_schema()
            },
            "required": ["user_id"],
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # TODO:
        # 1. Get user `id` from `arguments`
        # 2. Get `new_info` from `arguments` and create `UserUpdate` via pydentic `UserUpdate.model_validate`
        # 3. Call user_client update_user and return its results
        # 4. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
        print(f"=> Executing {self.name} with arguments: {arguments}")
        user_id = arguments.get("user_id")
        new_info = arguments.get("new_info")
        user_info = UserUpdate.model_validate(new_info)
        return self._user_client.update_user(user_id, user_info)
