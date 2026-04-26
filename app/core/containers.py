from functools import lru_cache

import punq

from app.core.settings import settings
from app.services.auth import AbstractAuthService, AuthService
from app.services.cart_items import AbstractCartItemService, CartItemService
from app.services.carts import AbstractCartService, CartService
from app.services.categories import AbstractCategoryService, CategoryService
from app.services.faq import AbstractFAQService, FAQService
from app.services.files import AbstractFileStorageService, LocalFileStorage, SupabaseFileStorage
from app.services.likes import AbstractLikeService, LikeService
from app.services.messages import AbstractMessageService, MessageService
from app.services.orders import AbstractOrderService, OrderService
from app.services.product_images import AbstractProductImageService, ProductImageService
from app.services.products import AbstractProductService, ProductService
from app.services.tokens import AbstractJWTTokenService, JWTTokenService
from app.services.unique_products import AbstractUniqueProductService, UniqueProductService
from app.services.users import AbstractUserService, UserService
from app.services.website_settings import AbstractWebSiteSettingsService, WebSiteSettingsService
from app.use_cases.auth.login import LoginUserUseCase
from app.use_cases.auth.refresh import RefreshTokenUseCase
from app.use_cases.auth.registration import RegisterUserUseCase
from app.use_cases.cart.change_items_quantity import AbstractChangeItemQuantityUseCase, ChangeItemQuantityUseCase
from app.use_cases.cart.create import AbstractCreateCartUseCase, CreateCartUseCase
from app.use_cases.cart.create_cart_item import AbstractAddToCartUseCase, AddToCartUseCase
from app.use_cases.cart.delete_item import AbstractDeleteFromCartUseCase, DeleteFromCartUseCase
from app.use_cases.cart.fetch import AbstractFetchCartUseCase, FetchCartUseCase
from app.use_cases.cart.merge import AbstractMergeCartsUseCase, MergeCartsUseCase
from app.use_cases.categories.create import AbstractCreateCategoryUseCase, CreateCategoryUseCase
from app.use_cases.categories.delete import AbstractDeleteCategoryUseCase, DeleteCategoryUseCase
from app.use_cases.categories.fetch_all import AbstractFetchCategoriesUseCase, FetchCategoriesUseCase
from app.use_cases.categories.fetch_children import AbstractFetchChildCategoriesUseCase, FetchChildCategoriesUseCase
from app.use_cases.categories.get_names_from_slugs import AbstractFetchNamesFromSlugsUseCase, FetchNamesFromSlugsUseCase
from app.use_cases.categories.update import AbstractUpdateCategoryUseCase, UpdateCategoryUseCase
from app.use_cases.faq.create import AbstractCreateFAQUseCase, CreateFAQUseCase
from app.use_cases.faq.delete import AbstractDeleteFAQUseCase, DeleteFAQUseCase
from app.use_cases.faq.fetch_all import AbstractFetchFAQsUseCase, FetchFAQsUseCase
from app.use_cases.faq.fetch_one import AbstractFetchFAQUseCase, FetchFAQUseCase
from app.use_cases.faq.update import AbstractUpdateFAQUseCase, UpdateFAQUseCase
from app.use_cases.like.create import AbstractCreateLikeUseCase, CreateLikeUseCase
from app.use_cases.like.delete import AbstractDeleteLikeUseCase, DeleteLikeUseCase
from app.use_cases.like.fetch_all import AbstractFetchLikesUseCase, FetchLikesUseCase
from app.use_cases.like.fetch_liked_products import AbstractFetchLikedProductsUseCase, FetchLikedProductsUseCase
from app.use_cases.messages.change_message_status import AbstractChangeMessageStatusUseCase, ChangeMessageStatusUseCase
from app.use_cases.messages.create_messages import AbstractCreateMessageUseCase, CreateMessageUseCase
from app.use_cases.messages.delete import AbstractDeleteMessageUseCase, DeleteMessageUseCase
from app.use_cases.messages.fetch_message import AbstractFetchMessageUseCase, FetchMessageUseCase
from app.use_cases.messages.fetch_messages import AbstractFetchMessagesUseCase, FetchMessagesUseCase
from app.use_cases.orders.active import AbstractFetchActiveOrdersUseCase, FetchActiveOrdersUseCase
from app.use_cases.orders.create import AbstractCreateOrderUseCase, CreateOrderUseCase
from app.use_cases.orders.fetch_all import AbstractFetchOrdersUseCase, FetchOrdersUseCase
from app.use_cases.orders.fetch_customers import AbstractFetchCustomersUseCase, FetchCustomersUseCase
from app.use_cases.orders.history import AbstractFetchOrdersHistoryUseCase, FetchOrdersHistoryUseCase
from app.use_cases.orders.update import AbstractUpdateOrderUseCase, UpdateOrderUseCase
from app.use_cases.products.create import AbstractCreateProductUseCase, CreateProductUseCase
from app.use_cases.products.fetch_absolute_one import AbstractFetchAbsoluteProductUseCase, FetchAbsoluteProductUseCase
from app.use_cases.products.fetch_all import AbstractFetchProductsUseCase, FetchProductsUseCase
from app.use_cases.products.fetch_by_ids import AbstractFetchProductsByIdsUseCase, FetchProductsByIdsUseCase
from app.use_cases.products.fetch_filters import AbstractFetchFiltersUseCase, FetchFiltersUseCase
from app.use_cases.products.fetch_popular import AbstractFetchPopularProductsUseCase, FetchPopularProductsUseCase
from app.use_cases.products.unique.delete_unique import AbstractDeleteUniqueProductUseCase, DeleteUniqueProductUseCase
from app.use_cases.products.unique.fetch_all import AbstractFetchUniqueProductsUseCase, FetchUniqueProductsUseCase
from app.use_cases.products.update import AbstractUpdateProductUseCase, UpdateProductUseCase
from app.use_cases.users.update import AbstractUpdateUserUseCase, UpdateUserUseCase
from app.use_cases.website_settings.fetch import AbstractFetchWebSiteSettingsUseCase, FetchWebSiteSettingsUseCase
from app.use_cases.website_settings.update import AbstractUpdateWebSiteSettingsUseCase, UpdateWebSiteSettingsUseCase


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    if settings.environment != "prod":
        container.register(AbstractFileStorageService, LocalFileStorage)
    else:
        container.register(AbstractFileStorageService, SupabaseFileStorage)

    # Auth
    container.register(AbstractAuthService, AuthService)
    container.register(RegisterUserUseCase)
    container.register(LoginUserUseCase)
    container.register(RefreshTokenUseCase)

    # Cart
    container.register(AbstractCartService, CartService)
    container.register(AbstractCartItemService, CartItemService)
    container.register(AbstractFetchCartUseCase, FetchCartUseCase)
    container.register(AbstractCreateCartUseCase, CreateCartUseCase)
    container.register(AbstractMergeCartsUseCase, MergeCartsUseCase)
    container.register(AbstractAddToCartUseCase, AddToCartUseCase)
    container.register(AbstractDeleteFromCartUseCase, DeleteFromCartUseCase)
    container.register(AbstractChangeItemQuantityUseCase, ChangeItemQuantityUseCase)

    # Category
    container.register(AbstractCategoryService, CategoryService)
    container.register(AbstractFetchCategoriesUseCase, FetchCategoriesUseCase)
    container.register(AbstractFetchChildCategoriesUseCase, FetchChildCategoriesUseCase)
    container.register(AbstractCreateCategoryUseCase, CreateCategoryUseCase)
    container.register(AbstractUpdateCategoryUseCase, UpdateCategoryUseCase)
    container.register(AbstractDeleteCategoryUseCase, DeleteCategoryUseCase)
    container.register(AbstractFetchNamesFromSlugsUseCase, FetchNamesFromSlugsUseCase)

    # FAQ
    container.register(AbstractFAQService, FAQService)
    container.register(AbstractFetchFAQsUseCase, FetchFAQsUseCase)
    container.register(AbstractFetchFAQUseCase, FetchFAQUseCase)
    container.register(AbstractCreateFAQUseCase, CreateFAQUseCase)
    container.register(AbstractUpdateFAQUseCase, UpdateFAQUseCase)
    container.register(AbstractDeleteFAQUseCase, DeleteFAQUseCase)

    # Like
    container.register(AbstractLikeService, LikeService)
    container.register(AbstractCreateLikeUseCase, CreateLikeUseCase)
    container.register(AbstractDeleteLikeUseCase, DeleteLikeUseCase)
    container.register(AbstractFetchLikesUseCase, FetchLikesUseCase)
    container.register(AbstractFetchLikedProductsUseCase, FetchLikedProductsUseCase)

    # Message
    container.register(AbstractMessageService, MessageService)
    container.register(AbstractCreateMessageUseCase, CreateMessageUseCase)
    container.register(AbstractFetchMessagesUseCase, FetchMessagesUseCase)
    container.register(AbstractFetchMessageUseCase, FetchMessageUseCase)
    container.register(AbstractChangeMessageStatusUseCase, ChangeMessageStatusUseCase)
    container.register(AbstractDeleteMessageUseCase, DeleteMessageUseCase)

    # Product
    container.register(AbstractProductService, ProductService)
    container.register(AbstractUniqueProductService, UniqueProductService)
    container.register(AbstractProductImageService, ProductImageService)
    container.register(AbstractFetchProductsUseCase, FetchProductsUseCase)
    container.register(AbstractFetchFiltersUseCase, FetchFiltersUseCase)
    container.register(AbstractFetchProductsByIdsUseCase, FetchProductsByIdsUseCase)
    container.register(AbstractDeleteUniqueProductUseCase, DeleteUniqueProductUseCase)
    container.register(AbstractFetchUniqueProductsUseCase, FetchUniqueProductsUseCase)
    container.register(AbstractCreateProductUseCase, CreateProductUseCase)
    container.register(AbstractFetchAbsoluteProductUseCase, FetchAbsoluteProductUseCase)
    container.register(AbstractUpdateProductUseCase, UpdateProductUseCase)
    container.register(AbstractFetchPopularProductsUseCase, FetchPopularProductsUseCase)

    # User
    container.register(AbstractUserService, UserService)
    container.register(AbstractJWTTokenService, JWTTokenService)
    container.register(AbstractUpdateUserUseCase, UpdateUserUseCase)

    # Order
    container.register(AbstractOrderService, OrderService)
    container.register(AbstractFetchOrdersUseCase, FetchOrdersUseCase)
    container.register(AbstractCreateOrderUseCase, CreateOrderUseCase)
    container.register(AbstractFetchOrdersHistoryUseCase, FetchOrdersHistoryUseCase)
    container.register(AbstractFetchActiveOrdersUseCase, FetchActiveOrdersUseCase)
    container.register(AbstractUpdateOrderUseCase, UpdateOrderUseCase)
    container.register(AbstractFetchCustomersUseCase, FetchCustomersUseCase)

    # WebSiteSettings
    container.register(AbstractWebSiteSettingsService, WebSiteSettingsService)
    container.register(AbstractFetchWebSiteSettingsUseCase, FetchWebSiteSettingsUseCase)
    container.register(AbstractUpdateWebSiteSettingsUseCase, UpdateWebSiteSettingsUseCase)

    return container
