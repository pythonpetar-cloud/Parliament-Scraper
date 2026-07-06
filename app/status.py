jobs = {}


def create_job(job_id):
    jobs[job_id] = {
        "status": "created",
        "message": ""
    }


def update_job(job_id, status, message=""):
    jobs[job_id] = {
        "status": status,
        "message": message
    }


def get_job(job_id):
    return jobs.get(job_id)