from cloudMonitoring.structs.slottifier_entry import SlottifierEntry


def test_add():
    """
    test that adding two SlottifierEntry dataclasses works properly
    """
    fst = SlottifierEntry(
        slots_available=1,
        estimated_gpu_slots_used=1,
        max_gpu_slots_capacity=1,
        max_gpu_slots_capacity_enabled=1,
    )

    snd = SlottifierEntry(
        slots_available=2,
        estimated_gpu_slots_used=3,
        max_gpu_slots_capacity=4,
        max_gpu_slots_capacity_enabled=5,
    )

    assert fst + snd == SlottifierEntry(
        slots_available=3,
        estimated_gpu_slots_used=4,
        max_gpu_slots_capacity=5,
        max_gpu_slots_capacity_enabled=6,
    )
