from dataclasses import dataclass


@dataclass
class SlottifierEntry:
    """
    A dataclass to hold slottifier information
    :param slots_available: Number of slots available for a flavor
    :param estimated_gpu_slots_used: Number of gpu slots currently used that could host this flavor
    estimated by amount of cores/mem already used by hvs as there's no way in openstack to find this out directly
    :param max_gpu_slots_capacity: Number of gpus available on all compatible hypervisors to build this flavor on
    :param max_gpu_slots_capacity_enabled: like max_gpu_slots_capacity, but only counting hosts with nova-compute
    service enabled
    """

    slots_available: int = 0
    estimated_gpu_slots_used: int = 0
    max_gpu_slots_capacity: int = 0
    max_gpu_slots_capacity_enabled: int = 0

    def __add__(self, other):
        """
        dunder method to add two SlottifierEntry values together.
        :param other: Another SlottifierEntry dataclass to add
        :return: A SlottifierEntry dataclass where each attribute value from current dataclass and given dataclass are
        added together
        """
        if not isinstance(other, SlottifierEntry):
            raise TypeError(
                f"Unsupported operand type for +: '{type(self)}' and '{type(other)}'"
            )

        return SlottifierEntry(
            slots_available=self.slots_available + other.slots_available,
            estimated_gpu_slots_used=self.estimated_gpu_slots_used
            + other.estimated_gpu_slots_used,
            max_gpu_slots_capacity=self.max_gpu_slots_capacity
            + other.max_gpu_slots_capacity,
            max_gpu_slots_capacity_enabled=self.max_gpu_slots_capacity_enabled
            + other.max_gpu_slots_capacity_enabled,
        )
