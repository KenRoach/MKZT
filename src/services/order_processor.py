from typing import List, Dict, Any

class OrderProcessor:
    async def process_order_items(self, order_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process order items and create them in the database"""
        processed_items = []
        for item in items:
            try:
                # Create order item with description
                order_item = await self.crm_repo.create_order_item(
                    order_id=order_id,
                    item_name=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["price"],
                    description=item.get("description"),
                    special_instructions=item.get("special_instructions")
                )
                processed_items.append(order_item)
            except Exception as e:
                logger.error(f"Error processing order item: {str(e)}")
                raise
        return processed_items

    async def format_order_response(self, order: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format order response with item descriptions"""
        return {
            "order_id": order["id"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "items": [{
                "name": item["item_name"],
                "quantity": item["quantity"],
                "price": item["unit_price"],
                "description": item["description"],
                "special_instructions": item["special_instructions"]
            } for item in items],
            "created_at": order["created_at"]
        } 