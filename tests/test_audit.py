from voting_system.chain import append_event, verify_chain


def test_hash_chain_detects_tampering() -> None:
    events = []
    append_event(events, actor_role="main_admin", action="class_created", details={"class_id": "c1"})
    append_event(events, actor_role="faculty_officer", action="candidate_approved", details={"application_id": "a1"})
    assert verify_chain(events)
    events[1]["action"] = "candidate_rejected"
    assert not verify_chain(events)
