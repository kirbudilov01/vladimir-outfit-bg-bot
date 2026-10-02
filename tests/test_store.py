from app.db import Store


def test_job_stats(tmp_path):
    store = Store(str(tmp_path / "db.sqlite3"))
    assert store.stats() == {"jobs": 0, "users": 0}
    store.save_job(1, "input.jpg", "output.jpg")
    store.save_job(1, "input2.jpg", "output2.jpg")
    assert store.stats() == {"jobs": 2, "users": 1}
