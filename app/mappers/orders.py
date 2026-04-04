from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.mappers.products import ProductVariationReadMapper
from app.models.orders import Order, OrderItem
from app.schemas.orders import (
    CreateOrderItemSchema,
    CreateOrderSchema,
    ReadOrderBaseSchema,
    ReadOrderItemBaseSchema,
    ReadOrderItemSchema,
    ReadOrderSchema,
    UpdateOrderSchema,
)


class OrderBaseReadMapper(BaseReadMapper[Order, ReadOrderBaseSchema]):

    @staticmethod
    def to_dto(orm_obj: Order) -> ReadOrderBaseSchema:
        return ReadOrderBaseSchema(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            status=orm_obj.status,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            first_name=orm_obj.first_name,
            last_name=orm_obj.last_name,
            patronymic=orm_obj.patronymic,
            phone_number=orm_obj.phone_number,
            email=orm_obj.email,
            address=orm_obj.address,
            waybill_number=orm_obj.waybill_number,
            shipping_method=orm_obj.shipping_method,
            payment_method=orm_obj.payment_method,
            price_discount=(
                float(orm_obj.price_discount) if orm_obj.price_discount else 0.0
            ),
        )


# TODO: think about better solution, generic from parent class uses here
class OrderReadMapper(OrderBaseReadMapper):

    @staticmethod
    def to_dto(orm_obj: Order) -> ReadOrderSchema:
        base = OrderBaseReadMapper.to_dto(orm_obj)
        return ReadOrderSchema(
            **base.model_dump(),
            items=OrderItemReadMapper.to_dto_list(orm_obj.items),
        )


class OrderCreateMapper(BaseUpsertMapper[Order, CreateOrderSchema]):
    pass


class OrderUpdateMapper(BaseUpsertMapper[Order, UpdateOrderSchema]):
    pass


class OrderItemBaseReadMapper(BaseReadMapper[OrderItem, ReadOrderItemBaseSchema]):
    @staticmethod
    def to_dto(orm_obj: OrderItem) -> ReadOrderItemBaseSchema:
        return ReadOrderItemBaseSchema(
            id=orm_obj.id,
            order_id=orm_obj.order_id,
            quantity=orm_obj.quantity,
            price_at_order=orm_obj.price_at_order,
            product_id=orm_obj.product_id,
        )


class OrderItemReadMapper(OrderItemBaseReadMapper):
    @staticmethod
    def to_dto(orm_obj: OrderItem) -> ReadOrderItemSchema:
        base = OrderItemBaseReadMapper.to_dto(orm_obj)
        return ReadOrderItemSchema(
            **base.model_dump(),
            product=ProductVariationReadMapper.to_dto(orm_obj.product),  # TODO: also change related models with mappers
        )


class OrderItemCreateMapper(BaseUpsertMapper[OrderItem, CreateOrderItemSchema]):
    pass
