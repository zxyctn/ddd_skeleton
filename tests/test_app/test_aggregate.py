def test_aggregate_registers_event(agg, event):
    agg.register_event(event)
    events = agg.pop_events()

    assert len(events) == 1
    assert event in events
    assert len(agg.pop_events()) == 0
