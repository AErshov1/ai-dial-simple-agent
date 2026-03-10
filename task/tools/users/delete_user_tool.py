from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "delete_user"

    @property
    def description(self) -> str:
        return "Tool for deleting a user by their ID. It accepts the user ID as a parameter."

    @property
    def input_schema(self) -> dict[str, Any]:
        # Provide tool params Schema. This tool applies user `id` (number) as a parameter and it is required
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Unique identifier of the user to delete",
                    "minimum": 0
                }
            },
            "required": ["user_id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # 1. Get int `id` from arguments
        # 2. Call user_client delete_user and return its results
        # 3. Optional: You can wrap it with `try-except` and return error as string `f"Error while deleting user by id: {str(e)}"`

        print(f"Executing {self.name} with arguments: {arguments}")
        user_id = arguments.get("user_id")
        if user_id is None:
            raise ValueError("user_id is required")

        return self._user_client.delete_user(user_id)
