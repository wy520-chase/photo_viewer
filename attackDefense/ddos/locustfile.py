from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def index(self):
        self.client.get("/", headers={"Connection": "keep-alive"})