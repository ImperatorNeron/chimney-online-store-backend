from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.common import ItemNotFoundException
from app.schemas.orders import ReadExtendedOrderSchema, UpdateOrderItemQuantitySchema, UpdateOrderItemsSchema
from app.services.order_items import AbstractOrderItemService
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateOrderItemsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        order_id: int,
        items_in: UpdateOrderItemsSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadExtendedOrderSchema: ...


@dataclass
class UpdateOrderItemsUseCase(AbstractUpdateOrderItemsUseCase):

    order_service: AbstractOrderService
    order_item_service: AbstractOrderItemService

    async def execute(
        self,
        order_id: int,
        items_in: UpdateOrderItemsSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadExtendedOrderSchema:
        async with uow:
            order_dto = await self.order_service.get_order_with_items(
                order_id=order_id, uow=uow,
            )
            items_by_id = {item.id: item for item in order_dto.items}

            deleted_count = 0
            for action in items_in.items:
                item = items_by_id.get(action.item_id)
                if not item:
                    raise ItemNotFoundException(
                        {"item_id": "Позицію не знайдено"},
                        detail=f"Order item {action.item_id} not found",
                    )

                if action.action == "delete":
                    if len(order_dto.items) - deleted_count <= 1:
                        raise ItemNotFoundException(
                            {"item_id": "Не можна видалити останню позицію"},
                            detail="Cannot delete the last item",
                        )
                    await self.order_item_service.delete(uow=uow, id=action.item_id)
                    deleted_count += 1
                elif action.action == "update_quantity":
                    await self.order_item_service.update(
                        item_id=action.item_id,
                        item_in=UpdateOrderItemQuantitySchema(
                            quantity=action.quantity,
                            price_at_order=round(item.product_price * action.quantity, 2),
                        ),
                        uow=uow,
                    )

            updated_order = await self.order_service.get_order_with_items(
                order_id=order_id, uow=uow,
            )
            total_price = await self.order_service.get_total_price(updated_order.items)
            total_quantity = await self.order_service.get_total_quantity(updated_order.items)

            return ReadExtendedOrderSchema(
                **updated_order.model_dump(),
                total_price=total_price,
                total_quantity=total_quantity,
            )
