"""This Module contains helper functions which can be used within the package of this module or outside it's package"""

def get_default_dev_mode_col_mapping() -> dict:
    """Returns the default mapping of columns to override manual mapping on UI.

    **NOTE: Only a Dev who knows the exact column names and keys 
    used through the app must use this function where needed**

    Returns:
        dict: A dictionary of column names.
    """

    mapping_dict = {}
    mapping_dict["purchased_date"] = "purchase_date"
    mapping_dict["purchased_time"] = "purchase_time"
    mapping_dict["product"] = "product"
    mapping_dict["category"] = "category"
    mapping_dict["sub_category"] = "sub-category"
    mapping_dict["shop"] = "shop"
    mapping_dict["quantity"] = "quantity"
    mapping_dict["weight"] = "weight"
    mapping_dict["price"] = "price"
    mapping_dict["is_essential"] = "is_essential"

    return mapping_dict