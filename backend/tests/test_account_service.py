import uuid
from unittest.mock import MagicMock

import pytest

from app.services.account import delete_user_data, get_account_summary

USER_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")


def test_summary_reports_each_count():
    db = MagicMock()
    # Counted in this order: resumes, analyses, job descriptions.
    db.execute.return_value.scalar_one.side_effect = [2, 5, 1]

    summary = get_account_summary(db, USER_ID)

    assert summary.resumes == 2
    assert summary.analyses == 5
    assert summary.job_descriptions == 1


def test_delete_removes_analyses_first_and_commits_once():
    db = MagicMock()

    delete_user_data(db, USER_ID)

    statements = [str(call.args[0]) for call in db.execute.call_args_list]
    tables = [statement.split()[2] for statement in statements]
    assert tables == ["analyses", "job_descriptions", "resumes"]
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_delete_rolls_back_when_a_statement_fails():
    db = MagicMock()
    db.execute.side_effect = RuntimeError("database unavailable")

    with pytest.raises(RuntimeError):
        delete_user_data(db, USER_ID)

    db.rollback.assert_called_once()
    db.commit.assert_not_called()