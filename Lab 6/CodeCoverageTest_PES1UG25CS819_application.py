import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


def test_rejects_non_list_orders():
    with pytest.raises(ValueError):
        process_order_batch(({"paid": True},), 0.1)


def test_rejects_negative_tax_rate():
    with pytest.raises(ValueError):
        process_order_batch([], -0.01)


def test_skips_unpaid_order_and_returns_no_sale():
    result = process_order_batch([{"paid": False}], 0.1)

    assert result == {
        "total": 0.0,
        "status": "NO_SALE"
    }


def test_small_and_large_orders_with_customizations():
    orders = [
        {
            "paid": True,
            "size": "small",
            "is_member": True,
            "customizations": [
                {"type": "syrup", "cost": 1.0},
                {"type": "standard", "cost": 0.5}
            ]
        },
        {
            "paid": True,
            "size": "large",
            "is_member": False,
            "customizations": [
                {"type": "syrup", "cost": 2.0}
            ]
        }
    ]

    result = process_order_batch(orders, 0.1)

    assert result == {
        "total": 12.71,
        "status": "COMPLETED"
    }


def test_medium_default_size_and_customizations():
    result = process_order_batch([{"paid": True}], 0)

    assert result == {
        "total": 4.5,
        "status": "COMPLETED"
    }


def test_invalid_size():
    result = process_order_batch(
        [{"paid": True, "size": "extra-large"}],
        0.1
    )

    assert result == {
        "total": 0.0,
        "status": "NO_SALE"
    }


def test_negative_customization_cost():
    result = process_order_batch(
        [{
            "paid": True,
            "size": "small",
            "customizations": [
                {"type": "syrup", "cost": -1}
            ]
        }],
        0
    )

    assert result == {
        "total": 3.0,
        "status": "COMPLETED"
    }


def test_allergen_alert_handling():
    orders = [
        {
            "paid": True,
            "size": "small",
            "strict_allergy": False,
            "customizations": [
                {"type": "allergen_alert", "cost": 0}
            ]
        },
        {
            "paid": True,
            "size": "medium",
            "strict_allergy": True,
            "customizations": [
                {"type": "allergen_alert", "cost": 0}
            ]
        }
    ]

    result = process_order_batch(orders, 0)

    assert result == {
        "total": 3.0,
        "status": "COMPLETED"
    }


def test_more_than_four_rejections_trigger_audit():
    orders = [
        {"paid": True, "size": "invalid"}
        for _ in range(5)
    ]

    result = process_order_batch(orders, 0.1)

    assert result == {
        "total": 0.0,
        "status": "AUDIT_REJECTED"
    }


def test_espresso_machine_no_data():
    assert check_espresso_machine([]) == "NO_DATA"


def test_espresso_machine_optimal():
    assert check_espresso_machine(
        [[97.0, 95.0, 97.0], [96.0]]
    ) == "OPTIMAL"


def test_espresso_machine_shutdown():
    assert check_espresso_machine(
        [[97.0, 98.0]]
    ) == "SHUTDOWN"
