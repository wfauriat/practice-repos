import pytest
from pathlib import Path

from ..ingest import load_customers

def test_missing_source_raises_and_leaves_no_db(tmp_path):
    db = tmp_path / "test.db"
    with pytest.raises(FileNotFoundError) as excinfo:
        load_customers.main(["--src", str(tmp_path / "nofile"), "--db", str(db)])
    assert not db.exists()
    assert "nofile" in str(excinfo.value)




