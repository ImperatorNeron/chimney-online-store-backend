from typing import Type

from app.mappers.orders import OrderItemBaseReadMapper, OrderItemUpdateMapper
from app.schemas.orders import ReadOrderItemBaseSchema, UpdateOrderItemQuantitySchema
from app.services.base import AbstractDelete, AbstractUpdate, Delete, Update


class AbstractOrderItemService(
    AbstractUpdate[ReadOrderItemBaseSchema, UpdateOrderItemQuantitySchema],
    AbstractDelete,
):
    pass


class OrderItemService(
    AbstractOrderItemService,
    Update[ReadOrderItemBaseSchema, UpdateOrderItemQuantitySchema],
    Delete,
):
    repository_name: str = "order_item"
    read_update_mapper: Type[OrderItemBaseReadMapper] = OrderItemBaseReadMapper
    update_mapper: Type[OrderItemUpdateMapper] = OrderItemUpdateMapper
