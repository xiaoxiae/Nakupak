from app.main import spa_file


def test_spa_file_serves_existing_file(tmp_path):
    (tmp_path / "index.html").write_text("index")
    (tmp_path / "sw.js").write_text("sw")
    assert spa_file(tmp_path, "sw.js") == (tmp_path / "sw.js").resolve()


def test_spa_file_falls_back_to_index(tmp_path):
    (tmp_path / "index.html").write_text("index")
    assert spa_file(tmp_path, "settings") == (tmp_path / "index.html").resolve()


def test_spa_file_blocks_traversal(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("index")
    (tmp_path / "secret.txt").write_text("secret")
    assert spa_file(dist, "../secret.txt") == (dist / "index.html").resolve()
    assert spa_file(dist, "/etc/passwd") == (dist / "index.html").resolve()
