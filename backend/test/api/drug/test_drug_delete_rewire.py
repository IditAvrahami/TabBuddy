import os
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test",
)

from backend.models import DrugSchedule  # noqa: E402


def _make_payload(
    name: str,
    dependency_type: str = "absolute",
    absolute_time: str | None = "08:00",
    depends_on_schedule_id: int | None = None,
    drug_offset_minutes: int | None = None,
    meal_schedule_id: int | None = None,
    meal_offset_minutes: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "kind": "pill",
        "amount_per_dose": 1,
        "dependency_type": dependency_type,
    }
    if absolute_time is not None:
        payload["absolute_time"] = absolute_time
    if depends_on_schedule_id is not None:
        payload["depends_on_schedule_id"] = depends_on_schedule_id
    if drug_offset_minutes is not None:
        payload["drug_offset_minutes"] = drug_offset_minutes
    if meal_schedule_id is not None:
        payload["meal_schedule_id"] = meal_schedule_id
    if meal_offset_minutes is not None:
        payload["meal_offset_minutes"] = meal_offset_minutes
    return payload


def _create_drug(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    resp = client.post("/drug", json=payload)
    assert resp.status_code == 200, resp.json()
    result: dict[str, Any] = resp.json()
    return result


def _get_schedule(db: Session, schedule_id: int) -> DrugSchedule | None:
    db.expire_all()
    return db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id).first()


# ── Basic deletion (no dependents) ────────────────────────────────────────


def test_delete_no_dependents(test_client: TestClient, db_session: Session) -> None:
    drug_a = _create_drug(test_client, _make_payload("DrugA"))

    resp = test_client.delete(f"/drug-id/{drug_a['id']}")
    assert resp.status_code == 200

    assert _get_schedule(db_session, drug_a["id"]) is None


# ── Single child rewire (A -> B -> C, delete B) ──────────────────────────


def test_delete_with_single_child_rewires(
    test_client: TestClient, db_session: Session
) -> None:
    a = _create_drug(test_client, _make_payload("Vitamin", absolute_time="08:00"))
    b = _create_drug(
        test_client,
        _make_payload(
            "Antibiotic",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=30,
        ),
    )
    c = _create_drug(
        test_client,
        _make_payload(
            "Probiotic",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=b["id"],
            drug_offset_minutes=10,
        ),
    )

    resp = test_client.delete(f"/drug-id/{b['id']}")
    assert resp.status_code == 200

    sched_c = _get_schedule(db_session, c["id"])
    assert sched_c is not None
    assert sched_c.depends_on_schedule_id == a["id"]
    assert sched_c.drug_offset_minutes == 40  # 30 + 10
    assert sched_c.dependency_type.value == "drug"


# ── Multiple children (A -> B, A -> C; B and C depend on A which depends on X) ─


def test_delete_with_multiple_children(
    test_client: TestClient, db_session: Session
) -> None:
    x = _create_drug(test_client, _make_payload("RootDrug", absolute_time="07:00"))
    a = _create_drug(
        test_client,
        _make_payload(
            "MiddleDrug",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=x["id"],
            drug_offset_minutes=20,
        ),
    )
    b = _create_drug(
        test_client,
        _make_payload(
            "ChildB",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=10,
        ),
    )
    c = _create_drug(
        test_client,
        _make_payload(
            "ChildC",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=20,
        ),
    )

    resp = test_client.delete(f"/drug-id/{a['id']}")
    assert resp.status_code == 200

    sched_b = _get_schedule(db_session, b["id"])
    assert sched_b is not None
    assert sched_b.depends_on_schedule_id == x["id"]
    assert sched_b.drug_offset_minutes == 30  # 20 + 10

    sched_c = _get_schedule(db_session, c["id"])
    assert sched_c is not None
    assert sched_c.depends_on_schedule_id == x["id"]
    assert sched_c.drug_offset_minutes == 40  # 20 + 20


# ── Delete ABSOLUTE root with children → children become ABSOLUTE ─────────


def test_delete_absolute_root_with_children(
    test_client: TestClient, db_session: Session
) -> None:
    a = _create_drug(test_client, _make_payload("AbsRoot", absolute_time="08:00"))
    b = _create_drug(
        test_client,
        _make_payload(
            "DepChild",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=30,
        ),
    )

    resp = test_client.delete(f"/drug-id/{a['id']}")
    assert resp.status_code == 200

    sched_b = _get_schedule(db_session, b["id"])
    assert sched_b is not None
    assert sched_b.dependency_type.value == "absolute"
    assert sched_b.depends_on_schedule_id is None
    assert sched_b.drug_offset_minutes is None
    assert sched_b.absolute_time is not None
    assert sched_b.absolute_time.hour == 8
    assert sched_b.absolute_time.minute == 30


# ── Delete MEAL root with children → children become MEAL ─────────────────


def test_delete_meal_root_with_children(
    test_client: TestClient, db_session: Session
) -> None:
    meal_resp = test_client.post(
        "/meal-schedules", json={"meal_name": "Breakfast", "base_time": "07:00"}
    )
    assert meal_resp.status_code == 200
    meals = test_client.get("/meal-schedules").json()
    meal_id = next(m["id"] for m in meals if m["meal_name"] == "Breakfast")

    a = _create_drug(
        test_client,
        _make_payload(
            "MealRoot",
            dependency_type="meal",
            absolute_time=None,
            meal_schedule_id=meal_id,
            meal_offset_minutes=20,
        ),
    )
    b = _create_drug(
        test_client,
        _make_payload(
            "MealChild",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=10,
        ),
    )

    resp = test_client.delete(f"/drug-id/{a['id']}")
    assert resp.status_code == 200

    sched_b = _get_schedule(db_session, b["id"])
    assert sched_b is not None
    assert sched_b.dependency_type.value == "meal"
    assert sched_b.depends_on_schedule_id is None
    assert sched_b.drug_offset_minutes is None
    assert sched_b.meal_schedule_id == meal_id
    assert sched_b.meal_offset_minutes == 30  # 20 + 10


# ── Negative offsets ──────────────────────────────────────────────────────


def test_delete_negative_offset(test_client: TestClient, db_session: Session) -> None:
    a = _create_drug(test_client, _make_payload("DrugA_Neg", absolute_time="10:00"))
    b = _create_drug(
        test_client,
        _make_payload(
            "DrugB_Neg",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=-15,
        ),
    )
    c = _create_drug(
        test_client,
        _make_payload(
            "DrugC_Neg",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=b["id"],
            drug_offset_minutes=10,
        ),
    )

    resp = test_client.delete(f"/drug-id/{b['id']}")
    assert resp.status_code == 200

    sched_c = _get_schedule(db_session, c["id"])
    assert sched_c is not None
    assert sched_c.depends_on_schedule_id == a["id"]
    assert sched_c.drug_offset_minutes == -5  # -15 + 10


# ── Dependents preview endpoint ──────────────────────────────────────────


def test_dependents_endpoint_returns_preview(
    test_client: TestClient,
) -> None:
    a = _create_drug(test_client, _make_payload("PreviewA", absolute_time="08:00"))
    _create_drug(
        test_client,
        _make_payload(
            "PreviewB",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=30,
        ),
    )

    resp = test_client.get(f"/drug-id/{a['id']}/dependents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_dependents"] is True
    assert len(data["dependents"]) == 1

    dep = data["dependents"][0]
    assert dep["drug_name"] == "PreviewB"
    assert dep["current_depends_on_name"] == "PreviewA"
    assert dep["current_offset_minutes"] == 30
    assert dep["new_dependency_type"] == "absolute"
    assert dep["new_absolute_time"] == "08:30"


def test_dependents_endpoint_no_deps(test_client: TestClient) -> None:
    a = _create_drug(test_client, _make_payload("LonelyDrug", absolute_time="09:00"))

    resp = test_client.get(f"/drug-id/{a['id']}/dependents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_dependents"] is False
    assert data["dependents"] == []


def test_dependents_endpoint_not_found(test_client: TestClient) -> None:
    resp = test_client.get("/drug-id/99999/dependents")
    assert resp.status_code == 404


# ── Dependents preview for drug-chain rewire ──────────────────────────────


def test_dependents_endpoint_drug_chain_preview(
    test_client: TestClient,
) -> None:
    a = _create_drug(test_client, _make_payload("ChainA", absolute_time="08:00"))
    b = _create_drug(
        test_client,
        _make_payload(
            "ChainB",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=30,
        ),
    )
    _create_drug(
        test_client,
        _make_payload(
            "ChainC",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=b["id"],
            drug_offset_minutes=10,
        ),
    )

    resp = test_client.get(f"/drug-id/{b['id']}/dependents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_dependents"] is True

    dep = data["dependents"][0]
    assert dep["drug_name"] == "ChainC"
    assert dep["new_dependency_type"] == "drug"
    assert dep["new_depends_on_name"] == "ChainA"
    assert dep["new_offset_minutes"] == 40  # 30 + 10


# ── Verify deleted schedule is removed from DB ───────────────────────────


def test_deleted_schedule_removed_from_db(
    test_client: TestClient, db_session: Session
) -> None:
    a = _create_drug(test_client, _make_payload("ToDelete", absolute_time="08:00"))
    b = _create_drug(
        test_client,
        _make_payload(
            "Survivor",
            dependency_type="drug",
            absolute_time=None,
            depends_on_schedule_id=a["id"],
            drug_offset_minutes=15,
        ),
    )

    test_client.delete(f"/drug-id/{a['id']}")

    assert _get_schedule(db_session, a["id"]) is None
    assert _get_schedule(db_session, b["id"]) is not None
