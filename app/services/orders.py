from abc import abstractmethod
from typing import Optional, Type

from app.mappers.orders import (
    CustomerReadMapper,
    OrderBaseReadMapper,
    OrderCreateMapper,
    OrderItemBaseReadMapper,
    OrderItemCreateMapper,
    OrderReadMapper,
    OrderUpdateMapper,
)
from app.schemas.filters import CustomerFiltersSchema, CustomerSortOrderSchema
from app.schemas.orders import (
    CreateOrderItemSchema,
    CreateOrderSchema,
    ReadCustomerSchema,
    ReadOrderBaseSchema,
    ReadOrderItemBaseSchema,
    ReadOrderItemSchema,
    ReadOrderSchema,
    UpdateOrderSchema,
)
from app.services.base import AbstractCount, AbstractCreate, AbstractRead, AbstractUpdate, Count, Create, Read, Update
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractOrderService(
    AbstractRead[ReadOrderSchema],
    AbstractCreate[ReadOrderBaseSchema, CreateOrderSchema],
    AbstractUpdate[ReadOrderBaseSchema, UpdateOrderSchema],
    AbstractCount,
):

    @abstractmethod
    async def get_order_history(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
        limit: int = None,
        offset: int = None,
    ) -> list[ReadOrderSchema]: ...

    @abstractmethod
    async def get_active_orders(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
        limit: int = None,
        offset: int = None,
    ) -> list[ReadOrderSchema]: ...

    @abstractmethod
    async def get_total_price(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> float: ...

    @abstractmethod
    async def get_total_quantity(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> int: ...

    @abstractmethod
    async def bulk_create(
        self,
        cart_items: list[CreateOrderItemSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderItemBaseSchema]: ...

    @abstractmethod
    async def get_customers(
        self, uow: AbstractUnitOfWork,
        filters: Optional[CustomerFiltersSchema] = None,
        sort_params: Optional[CustomerSortOrderSchema] = None,
        limit: int = 20, offset: int = 0,
    ) -> list[ReadCustomerSchema]: ...

    @abstractmethod
    async def get_customers_count(
        self, uow: AbstractUnitOfWork,
        filters: Optional[CustomerFiltersSchema] = None,
    ) -> int: ...


class OrderService(
    AbstractOrderService,
    Read[ReadOrderSchema],
    Create[ReadOrderBaseSchema, CreateOrderSchema],
    Update[ReadOrderBaseSchema, UpdateOrderSchema],
    Count,
):
    repository_name: str = "order"
    read_mapper: Type[OrderReadMapper] = OrderReadMapper
    _read_mapper: Type[OrderBaseReadMapper] = OrderBaseReadMapper
    read_create_mapper = read_update_mapper = _read_mapper
    create_mapper: Type[OrderCreateMapper] = OrderCreateMapper
    update_mapper: Type[OrderUpdateMapper] = OrderUpdateMapper

    async def get_order_history(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
        limit: int = None,
        offset: int = None,
    ) -> list[ReadOrderSchema]:
        return self.read_mapper.to_dto_list(
            await uow.order.finished_orders_by_user_id(user_id=user_id, limit=limit, offset=offset),
        )

    async def get_active_orders(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
        limit: int = None,
        offset: int = None,
    ) -> list[ReadOrderSchema]:
        return self.read_mapper.to_dto_list(
            await uow.order.current_orders_by_user_id(user_id=user_id, limit=limit, offset=offset),
        )

    async def get_total_price(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> float:
        return round(sum(item.price_at_order for item in order_items))

    async def get_total_quantity(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> int:
        return sum(item.quantity for item in order_items)

    async def bulk_create(
        self,
        items: list[CreateOrderItemSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderItemBaseSchema]:
        return OrderItemBaseReadMapper.to_dto_list(
            await uow.order_item.bulk_create(
                data_list=OrderItemCreateMapper.to_model_list(items),
            ),
        )

    async def get_customers(
        self, uow: AbstractUnitOfWork,
        filters: Optional[CustomerFiltersSchema] = None,
        sort_params: Optional[CustomerSortOrderSchema] = None,
        limit: int = 20, offset: int = 0,
    ) -> list[ReadCustomerSchema]:
        filters_dict = filters.model_dump() if filters else {}
        order_by = sort_params.field if sort_params else "last_order_at"
        ordering = sort_params.ordering if sort_params else "desc"
        return CustomerReadMapper.to_dto_list(
            await uow.order.get_customers(
                limit=limit, offset=offset,
                order_by=order_by, ordering=ordering,
                **filters_dict,
            ),
        )

    async def get_customers_count(
        self, uow: AbstractUnitOfWork, filters: Optional[CustomerFiltersSchema] = None,
    ) -> int:
        filters_dict = filters.model_dump() if filters else {}
        return await uow.order.get_customers_count(**filters_dict)
