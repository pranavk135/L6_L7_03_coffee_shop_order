import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


def test_validation_rejects_non_list():
    with pytest.raises(ValueError):
        process_order_batch(({"paid": True},), 0.1)


def test_validation_rejects_negative_tax_rate():
    with pytest.raises(ValueError):
        process_order_batch([], -0.01)


def test_empty_batch_returns_no_sale():
    assert process_order_batch([], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_unpaid_order_is_skipped():
    assert process_order_batch([{"paid": False}], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


@pytest.mark.parametrize(
    "size, expected",
    [("small", 3.0), ("medium", 4.5), ("large", 6.0)],
)
def test_each_valid_size(size, expected):
    assert process_order_batch([{"paid": True, "size": size}], 0.0) == {
        "total": expected, "status": "COMPLETED"
    }


def test_missing_size_defaults_to_medium():
    assert process_order_batch([{"paid": True}], 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_invalid_size_is_rejected():
    assert process_order_batch([{"paid": True, "size": "extra-large"}], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_negative_customization_cost_is_rejected():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": -1.0},
            {"type": "other", "cost": 0.5},
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.5, "status": "COMPLETED"
    }


def test_syrup_cost_at_or_below_cap():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": 1.5}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_syrup_cost_above_cap_is_capped():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": 2.0}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_other_customization_adds_cost():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "extra_shot", "cost": 0.75}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.75, "status": "COMPLETED"
    }


def test_allergen_alert_non_strict():
    orders = [{
        "paid": True,
        "size": "small",
        "strict_allergy": False,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "extra_shot", "cost": 0.5}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.5, "status": "COMPLETED"
    }


def test_allergen_alert_strict():
    orders = [{
        "paid": True,
        "size": "small",
        "strict_allergy": True,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "extra_shot", "cost": 10.0}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_member_discount_and_non_member_path():
    orders = [
        {"paid": True, "size": "small", "is_member": True},
        {"paid": True, "size": "small", "is_member": False},
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 5.7, "status": "COMPLETED"
    }


def test_tax_is_applied():
    assert process_order_batch(
        [{"paid": True, "size": "small"}], 0.1
    ) == {
        "total": 3.3, "status": "COMPLETED"
    }


def test_more_than_four_rejections_trigger_audit():
    orders = [
        {"paid": True, "size": "unknown"}
        for _ in range(5)
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "AUDIT_REJECTED"
    }


def test_four_rejections_do_not_trigger_audit():
    orders = [
        {"paid": True, "size": "unknown"}
        for _ in range(4)
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_espresso_empty_input():
    assert check_espresso_machine([]) == "NO_DATA"


def test_espresso_normal_temperatures():
    assert check_espresso_machine(
        [[97.0, 96.0, 97.0], [96.0]]
    ) == "OPTIMAL"


def test_espresso_one_overheat():
    assert check_espresso_machine(
        [[97.0]]
    ) == "OPTIMAL"


def test_espresso_two_consecutive_overheats():
    assert check_espresso_machine(
        [[97.0, 98.0]]
    ) == "SHUTDOWN"


def test_espresso_shutdown_in_later_cycle():
    assert check_espresso_machine(
        [[97.0, 96.0], [97.0, 97.0]]
    ) == "SHUTDOWN"


def test_espresso_empty_cycle():
    assert check_espresso_machine([[]]) == "OPTIMAL"
from coffee_shop_order import process_order_batch, check_espresso_machine


def test_validation_rejects_non_list():
    with pytest.raises(ValueError):
        process_order_batch(({"paid": True},), 0.1)


def test_validation_rejects_negative_tax_rate():
    with pytest.raises(ValueError):
        process_order_batch([], -0.01)


def test_empty_batch_returns_no_sale():
    assert process_order_batch([], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_unpaid_order_is_skipped():
    assert process_order_batch([{"paid": False}], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


@pytest.mark.parametrize(
    "size, expected",
    [("small", 3.0), ("medium", 4.5), ("large", 6.0)],
)
def test_each_valid_size(size, expected):
    assert process_order_batch([{"paid": True, "size": size}], 0.0) == {
        "total": expected, "status": "COMPLETED"
    }


def test_missing_size_defaults_to_medium():
    assert process_order_batch([{"paid": True}], 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_invalid_size_is_rejected():
    assert process_order_batch([{"paid": True, "size": "extra-large"}], 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_negative_customization_cost_is_rejected():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": -1.0},
            {"type": "other", "cost": 0.5},
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.5, "status": "COMPLETED"
    }


def test_syrup_cost_at_or_below_cap():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": 1.5}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_syrup_cost_above_cap_is_capped():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "syrup", "cost": 2.0}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 4.5, "status": "COMPLETED"
    }


def test_other_customization_adds_cost():
    orders = [{
        "paid": True,
        "size": "small",
        "customizations": [
            {"type": "extra_shot", "cost": 0.75}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.75, "status": "COMPLETED"
    }


def test_allergen_alert_non_strict():
    orders = [{
        "paid": True,
        "size": "small",
        "strict_allergy": False,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "extra_shot", "cost": 0.5}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 3.5, "status": "COMPLETED"
    }


def test_allergen_alert_strict():
    orders = [{
        "paid": True,
        "size": "small",
        "strict_allergy": True,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "extra_shot", "cost": 10.0}
        ]
    }]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_member_discount_and_non_member_path():
    orders = [
        {"paid": True, "size": "small", "is_member": True},
        {"paid": True, "size": "small", "is_member": False},
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 5.7, "status": "COMPLETED"
    }


def test_tax_is_applied():
    assert process_order_batch(
        [{"paid": True, "size": "small"}], 0.1
    ) == {
        "total": 3.3, "status": "COMPLETED"
    }


def test_more_than_four_rejections_trigger_audit():
    orders = [
        {"paid": True, "size": "unknown"}
        for _ in range(5)
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "AUDIT_REJECTED"
    }


def test_four_rejections_do_not_trigger_audit():
    orders = [
        {"paid": True, "size": "unknown"}
        for _ in range(4)
    ]

    assert process_order_batch(orders, 0.0) == {
        "total": 0.0, "status": "NO_SALE"
    }


def test_espresso_empty_input():
    assert check_espresso_machine([]) == "NO_DATA"


def test_espresso_normal_temperatures():
    assert check_espresso_machine(
        [[97.0, 96.0, 97.0], [96.0]]
    ) == "OPTIMAL"


def test_espresso_one_overheat():
    assert check_espresso_machine(
        [[97.0]]
    ) == "OPTIMAL"


def test_espresso_two_consecutive_overheats():
    assert check_espresso_machine(
        [[97.0, 98.0]]
    ) == "SHUTDOWN"


def test_espresso_shutdown_in_later_cycle():
    assert check_espresso_machine(
        [[97.0, 96.0], [97.0, 97.0]]
    ) == "SHUTDOWN"


def test_espresso_empty_cycle():
    assert check_espresso_machine([[]]) == "OPTIMAL"
