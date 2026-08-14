from locust import HttpUser, task, between

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb2hpdCIsImV4cCI6MTc4NjY4NzY4OX0.r7XqXeO4QWg6S6T4fie46ho_WJvDjpd_-vSBJ1UNOqk"

class RateLimitUser(HttpUser):
    wait_time = between(0, 0.1)

    @task
    def get_data(self):
        self.client.get(
            "/api/data",
            headers={
                "Authorization": f"Bearer {TOKEN}"
            }
        )