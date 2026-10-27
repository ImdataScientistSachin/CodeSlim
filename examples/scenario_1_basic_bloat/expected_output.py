def calculate_total(items: list[dict]) -> float:
    total = 0.0
    if items:
        for item in items:
            if "price" in item and "quantity" in item:
                total += float(item["price"]) * int(item["quantity"])
    return total
